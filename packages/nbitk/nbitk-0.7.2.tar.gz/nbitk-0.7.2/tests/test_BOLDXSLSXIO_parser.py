import pytest
import pandas as pd
from Bio.Phylo import BaseTree
from nbitk.Taxon import Taxon
from nbitk.Phylo.BOLDXLSXIO import Parser


@pytest.fixture
def sample_excel_file(tmp_path):
    df_lab_sheet = pd.DataFrame({
        'Sample ID': ['S1', 'S2', 'S3', 'S4'],
        'Process ID': ['P1', 'P2', 'P3', 'P4'],
    })
    df_taxonomy = pd.DataFrame({
        'Sample ID': ['S1', 'S2', 'S3', 'S4'],
        'Phylum': ['Chordata', 'Chordata', 'Arthropoda', 'Chordata'],
        'Class': ['Mammalia', 'Mammalia', 'Insecta', 'Mammalia'],
        'Order': ['Primates', 'Carnivora', 'Coleoptera', 'Primates'],
        'Family': ['Hominidae', 'Felidae', 'Carabidae', 'Hominidae'],
        'Subfamily': ['', '', '', ''],
        'Tribe': ['', '', '', ''],
        'Genus': ['Homo', 'Felis', 'Carabus', 'Homo'],
        'Species': ['Homo sapiens', 'Felis catus', 'Carabus coriaceus', ''],
        'Subspecies': ['', '', '', '']
    })

    file_path = tmp_path / "test_bold.xlsx"
    with pd.ExcelWriter(file_path) as writer:
        df_lab_sheet.to_excel(writer, sheet_name='Lab Sheet', index=False, startrow=2)
        df_taxonomy.to_excel(writer, sheet_name='Taxonomy', index=False, startrow=2)

    return file_path


def test_tree_topology(sample_excel_file):
    parser = Parser(sample_excel_file)
    tree = parser.parse()

    # Check root
    assert isinstance(tree, BaseTree.Tree)
    assert isinstance(tree.root, Taxon)
    assert tree.root.name == "Root"

    # Check phyla
    phyla = list(tree.root.clades)
    assert len(phyla) == 2
    assert {p.name for p in phyla} == {"Chordata", "Arthropoda"}

    # Check Chordata lineage
    chordata = next(p for p in phyla if p.name == "Chordata")
    assert len(chordata.clades) == 1
    mammalia = chordata.clades[0]
    assert mammalia.name == "Mammalia"
    assert len(mammalia.clades) == 2
    assert {o.name for o in mammalia.clades} == {"Primates", "Carnivora"}

    # Check Homo sapiens
    primates = next(o for o in mammalia.clades if o.name == "Primates")
    hominidae = primates.clades[0]
    homo = hominidae.clades[0]
    homo_sapiens = homo.clades[0]
    assert homo_sapiens.name == "Homo sapiens"
    assert homo_sapiens.guids == {"P1": "S1"}
    assert homo.guids == {"P4": "S4"}

    # Check Arthropoda lineage
    arthropoda = next(p for p in phyla if p.name == "Arthropoda")
    insecta = arthropoda.clades[0]
    coleoptera = insecta.clades[0]
    carabidae = coleoptera.clades[0]
    carabus = carabidae.clades[0]
    carabus_coriaceus = carabus.clades[0]
    assert carabus_coriaceus.name == "Carabus coriaceus"
    assert carabus_coriaceus.guids == {"P3": "S3"}

    # Ensure no duplication
    all_nodes = list(tree.find_clades())
    assert len(all_nodes) == len(set(node.name for node in all_nodes))


if __name__ == "__main__":
    pytest.main()