import pandas as pd
from Bio.Phylo import BaseTree
from nbitk.Taxon import Taxon


"""
This class operates like the tree parsers in Bio.Phylo, but it is specifically designed to parse
the Excel files provided by the Barcode of Life Data Systems (BOLD) platform. The Excel file must
contain two tabs: 'Lab Sheet' and 'Taxonomy'. The 'Lab Sheet' tab must contain two columns:
'Sample ID' and 'Process ID'. The 'Taxonomy' tab must contain columns for the taxonomic ranks
(Phylum, Class, Order, Family, Subfamily, Tribe, Genus, Species, Subspecies). The parser will
create a tree with the taxonomic ranks as nodes and the sample IDs as leaves. The tree will be
returned as a BaseTree object but its nodes will be Taxon objects.

Usage:

from nbitk.Phylo.BOLDXLSXIO import Parser
parser = Parser('/path/to/bold.xlsx')
tree = parser.parse()
families = list(tree.find_clades({'taxonomic_rank':'family'}))
"""


def _create_tree() -> BaseTree.Tree:
    """Creates a BaseTree object with a root node."""
    root = Taxon(name="Root", taxonomic_rank="root")
    tree = BaseTree.Tree(root)
    return tree


def _graft_lineage(tree: BaseTree.Tree, lineage: list) -> Taxon:
    """
    Grafts a lineage onto the tree, avoiding duplication of terminal node names.
    Returns the terminal node, whether newly created or existing.
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
    def __init__(self, file):
        self.file = file

    def parse(self):
        # Read Excel file
        xl = pd.ExcelFile(self.file, engine="openpyxl")
        lab_sheet = pd.read_excel(xl, sheet_name="Lab Sheet", header=2)
        taxonomy = pd.read_excel(xl, sheet_name="Taxonomy", header=2)

        # Create mapping dict for Lab Sheet
        lab_mapping = dict(zip(lab_sheet["Sample ID"], lab_sheet["Process ID"]))

        # List of taxonomy columns
        taxonomy_columns = [
            "Phylum",
            "Class",
            "Order",
            "Family",
            "Subfamily",
            "Tribe",
            "Genus",
            "Species",
            "Subspecies",
        ]

        # Create tree
        tree = _create_tree()

        # Populate taxonomy tree
        for _, row in taxonomy.iterrows():
            sample_id = row["Sample ID"]
            lineage = []

            # Create Taxon objects for each level in the lineage
            for col in taxonomy_columns:
                if pd.notna(row[col]) and row[col] != "":
                    taxon = Taxon(taxonomic_rank=col.lower(), name=row[col])
                    lineage.append(taxon)

            # Graft the lineage onto the tree and append annotation only if it's a new tip
            tip = _graft_lineage(tree, lineage)
            process_id = lab_mapping[sample_id]
            tip.guids[process_id] = sample_id

        return tree
