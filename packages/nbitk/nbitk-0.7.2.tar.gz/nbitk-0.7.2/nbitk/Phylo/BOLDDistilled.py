import pandas as pd
from Bio.Phylo import BaseTree
from nbitk.Taxon import Taxon


"""
This class operates like the tree parsers in Bio.Phylo, but it is specifically designed to parse
the TSV files provided by the Barcode of Life Data Systems (BOLD) platform's 'distilled' release (in source.zip). 
The parser will create a tree with the taxonomic ranks as nodes and the sample IDs as leaves. The tree will be
returned as a BaseTree object but its nodes will be Taxon objects.

Usage:

from nbitk.Phylo.BOLDDistilled import Parser
parser = Parser('/path/to/BOLDistilled_COI_Jul2025_TAXONOMY.tsv')
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
        # Read TSV file
        table = pd.read_table(self.file, sep="\t")

        # List of taxonomy columns
        taxonomy_columns = [
            "kingdom",
            "phylum",
            "class",
            "order",
            "family",
            "subfamily",
            "tribe",
            "genus",
            "species",
            "subspecies",
            "bin"
        ]

        # Create tree
        tree = _create_tree()

        # Populate taxonomy tree
        for _, row in table.iterrows():
            lineage = []

            # Create Taxon objects for each level in the lineage
            for col in taxonomy_columns:
                if pd.notna(row[col]) and row[col] != "":
                    taxon = Taxon(taxonomic_rank=col.lower(), name=row[col])
                    lineage.append(taxon)

            # Graft the lineage onto the tree and append annotation only if it's a new tip
            tip = _graft_lineage(tree, lineage)

        return tree
