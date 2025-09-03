import os
import pytest
from Bio.Phylo import BaseTree
from nbitk.Phylo.DwCATaxonomyIO import Parser
from nbitk.Taxon import Taxon

# Fixture to provide the full path to the DarwinCore Archive test file.
@pytest.fixture
def dwca_file():
    # This constructs the file path relative to the tests directory.
    return os.path.join(os.path.dirname(__file__), "data", "nsr-20250207.dwca.zip")

# Fixture to parse the DarwinCore Archive and return the tree.
@pytest.fixture
def parsed_tree(dwca_file):
    parser = Parser(dwca_file)
    tree = parser.parse()
    return tree

def test_parse_returns_tree(parsed_tree):
    """
    Test that parsing the DarwinCore Archive returns a Bio.Phylo BaseTree.Tree,
    with a root node that is a Taxon named "Root" with taxonomic_rank "root".
    """
    assert isinstance(parsed_tree, BaseTree.Tree)
    root = parsed_tree.root
    assert isinstance(root, Taxon)
    assert root.name == "Root"
    assert root.taxonomic_rank == "root"

def test_tree_has_children(parsed_tree):
    """
    Test that the tree has been populated with child nodes (i.e., the root has at least one clade).
    """
    root = parsed_tree.root
    assert root.clades, "The tree root should have at least one child clade."

def test_all_nodes_are_taxa(parsed_tree):
    """
    Recursively ensure that every node in the tree is an instance of Taxon.
    """
    def check_node(node):
        assert isinstance(node, Taxon), f"Node {node} is not an instance of Taxon."
        for child in node.clades:
            check_node(child)
    check_node(parsed_tree.root)

def test_find_clades_by_rank(parsed_tree):
    """
    Verify that using find_clades with a filter (e.g., taxonomic_rank='family')
    returns a list. (It may be empty if no such rank exists in the test data.)
    """
    family_clades = list(parsed_tree.find_clades({'taxonomic_rank': 'family'}))
    assert isinstance(family_clades, list)

def test_leaf_nodes_have_guids(parsed_tree):
    """
    Recursively check that each leaf node (i.e., a node with no children) has
    a non-empty 'guids' dictionary attribute.
    """
    def check_leaf(node):
        if not node.clades:  # Leaf node
            # Assuming the parser attaches a 'guids' dict on tip nodes.
            assert hasattr(node, 'guids'), f"Leaf node {node.name} does not have a 'guids' attribute."
            assert node.guids, f"Leaf node {node.name} should have at least one guid."
        for child in node.clades:
            check_leaf(child)
    check_leaf(parsed_tree.root)
