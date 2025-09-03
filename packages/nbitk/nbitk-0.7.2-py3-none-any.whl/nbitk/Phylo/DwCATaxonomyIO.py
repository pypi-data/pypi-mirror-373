import zipfile
import xml.etree.ElementTree as ET
import pandas as pd
from io import StringIO

from Bio.Phylo import BaseTree
from nbitk.Taxon import Taxon


def _create_tree() -> BaseTree.Tree:
    """
    Creates a BaseTree.Tree object with a root Taxon.
    :return: BaseTree.Tree object
    """
    root = Taxon(name="Root", taxonomic_rank="root")
    tree = BaseTree.Tree(root)
    return tree


def _graft_lineage(tree: BaseTree.Tree, lineage: list) -> Taxon:
    """
    Grafts a lineage (a list of Taxon objects) onto the tree.
    At each level, if a child with the same name already exists,
    that node is used; otherwise the taxon is appended as a new clade.
    Returns the terminal (tip) node.
    :param tree: BaseTree.Tree object
    :param lineage: list of Taxon objects
    :return: Taxon object
    """
    node = tree.root
    for taxon in lineage:
        existing_node = next((child for child in node.clades if child.name == taxon.name), None)
        if existing_node:
            node = existing_node
        else:
            node.clades.append(taxon)
            node = taxon
    return node


class Parser:
    """
    This parser reads a zipped DarwinCore Archive and builds a Bio.Phylo BaseTree.Tree.

    The archive is expected to contain a DarwinCore meta.xml file and a core data file (e.g., Taxa.txt).
    The meta.xml file specifies attributes such as 'fieldsTerminatedBy' and 'ignoreHeaderLines'. Since
    the header row in the core file is skipped (per ignoreHeaderLines), the parser extracts the column
    names from meta.xml (using the <id> and <field> elements) and supplies them to pandas.

    The tree is built by using selected taxonomic columns from the core data. In this example, we use:

        ["kingdom", "phylum", "class", "order", "family", "genus", "subgenus", "specificEpithet", "infraspecificEpithet"]

    Each nonempty cell in these columns yields a Taxon node (with the column name used as the taxonomic_rank
    and the cell value as the Taxon name). The final (tip) node is annotated with its unique identifier,
    which in this archive is taken from the "taxonID" column.

    Usage:

        from nbitk.Phylo.DwCATaxonomyIO import Parser
        parser = Parser('/path/to/dwca.zip')
        tree = parser.parse()
        families = list(tree.find_clades({'taxonomic_rank': 'family'}))
    """

    def __init__(self, file):
        self.file = file

    def parse(self) -> BaseTree.Tree:
        """
        Parses the DarwinCore Archive and builds a Bio.Phylo BaseTree.Tree.
        :return: A BaseTree.Tree object.
        """
        # Open the zipped DarwinCore Archive.
        with zipfile.ZipFile(self.file, 'r') as zf:
            # Ensure meta.xml is present.
            if "meta.xml" not in zf.namelist():
                raise ValueError("The archive does not contain a meta.xml file.")
            meta_xml_data = zf.read("meta.xml")
            ns = {'dwc': 'http://rs.tdwg.org/dwc/text/'}
            root_meta = ET.fromstring(meta_xml_data)

            # Extract the core element.
            core_elem = root_meta.find('dwc:core', ns)
            if core_elem is None:
                raise ValueError("No core element found in meta.xml.")

            # Determine the core file location.
            location_elem = core_elem.find('dwc:files/dwc:location', ns)
            if location_elem is not None and location_elem.text:
                core_file_location = location_elem.text
            else:
                candidates = [name for name in zf.namelist() if name != "meta.xml"]
                if not candidates:
                    raise ValueError("No data file found in the archive.")
                core_file_location = candidates[0]

            # Get delimiter, encoding, and number of header lines to ignore.
            delimiter = core_elem.attrib.get("fieldsTerminatedBy", ",")
            if delimiter.lower() == "tab":
                delimiter = "\t"
            ignore_header_lines = int(core_elem.attrib.get("ignoreHeaderLines", "0"))
            encoding = core_elem.attrib.get("encoding", "UTF-8")

            # Extract column names from meta.xml.
            # Process the <id> element.
            id_elem = core_elem.find('dwc:id', ns)
            if id_elem is None:
                raise ValueError("No <id> element found in meta.xml core section.")
            id_index = int(id_elem.attrib.get("index", "0"))
            # We assign the id column the name "taxonID" (to match Taxa.txt).
            col_dict = {id_index: "taxonID"}

            # Process each <field> element.
            for field in core_elem.findall('dwc:field', ns):
                index = int(field.attrib["index"])
                term = field.attrib["term"]
                # Use the last part of the term URI as the column name.
                short_term = term.split("/")[-1]
                col_dict[index] = short_term

            # Build an ordered list of column names.
            max_index = max(col_dict.keys())
            ordered_names = [col_dict[i] for i in range(max_index + 1)]

            # Read and decode the core data file.
            core_data_bytes = zf.read(core_file_location)
            core_data = core_data_bytes.decode(encoding)
            # Since the header row is skipped (ignoreHeaderLines), supply the column names.
            df_core = pd.read_csv(
                StringIO(core_data),
                delimiter=delimiter,
                skiprows=ignore_header_lines,
                header=None,
                names=ordered_names
            )

            # Use "taxonID" as the unique identifier.
            if "taxonID" not in df_core.columns:
                raise ValueError("Expected column 'taxonID' not found in core data.")
            sample_id_col = "taxonID"

            # Define taxonomic columns to build the lineage.
            # Adjust this list as needed. Here we include several columns that
            # typically represent taxonomic ranks in DarwinCore data.
            taxonomy_columns = [
                "kingdom",
                "phylum",
                "class",
                "order",
                "family",
                "genus",
                "subgenus",
                "specificEpithet",
                "infraspecificEpithet"
            ]
            # Only include those columns that are present in the DataFrame.
            available_taxonomy_columns = [col for col in taxonomy_columns if col in df_core.columns]

            # Create the tree.
            tree = _create_tree()

            # Populate the tree by iterating over each row.
            for _, row in df_core.iterrows():
                sample_id = row[sample_id_col]
                lineage = []
                for col in available_taxonomy_columns:
                    if pd.notna(row[col]) and row[col] != "":
                        # For epithets, we want to combine with the genus.
                        if col in ("specificEpithet", "infraspecificEpithet"):
                            # First, try to locate the genus from the already built lineage.
                            genus = None
                            for tax in lineage:
                                # Here we assume the taxon created for the 'genus' column
                                # has taxonomic_rank "genus" (case-insensitive).
                                if tax.taxonomic_rank.lower() == "genus":
                                    genus = tax.name
                                    break

                            # Fallback: if not yet in the lineage, see if the row contains a valid 'genus' value.
                            if genus is None and "genus" in row and pd.notna(row["genus"]) and row["genus"] != "":
                                genus = str(row["genus"]).strip()

                            # If genus is still not found, you might choose to skip or use an empty string.
                            if genus is None:
                                genus = ""

                            # If we already created a (sub)species taxon (likely from a previous specificEpithet),
                            # then assume we are processing the infraspecificEpithet and simply append its value.
                            if lineage and lineage[-1].taxonomic_rank == "species":
                                # Append with a space (e.g., forming "Genus specificEpithet infraspecificEpithet").
                                lineage[-1].name += " " + str(row[col]).strip()
                            else:
                                # Otherwise, create a new Taxon.
                                # Combine the genus and the epithet to get a full binomial.
                                full_name = (genus + " " + str(row[col]).strip()).strip()
                                taxon = Taxon(taxonomic_rank="species", name=full_name)
                                lineage.append(taxon)
                        else:
                            # For all other columns, create the Taxon normally.
                            taxon = Taxon(taxonomic_rank=col, name=str(row[col]).strip())
                            lineage.append(taxon)

                tip = _graft_lineage(tree, lineage)
                # Annotate the tip node with its unique identifier.
                tip.guids['taxonID'] = sample_id

            return tree
