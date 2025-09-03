import pytest
from Bio.Phylo.BaseTree import Clade
from nbitk.Taxon import Taxon


@pytest.fixture
def taxon():
    return Taxon(
        name="Homo sapiens",
        common_name="Human",
        taxonomic_rank="species",
        taxonomic_authority="Linnaeus, 1758",
        taxonomic_code="ICZN",
        is_accepted=True,
        guids={"NCBI": "taxon:9606"},
        branch_length=0.1,
        confidence=0.95
    )


def test_initialization(taxon):
    assert taxon.name == "Homo sapiens"
    assert taxon.common_name == "Human"
    assert taxon.taxonomic_rank == "species"
    assert taxon.taxonomic_authority == "Linnaeus, 1758"
    assert taxon.taxonomic_code == "ICZN"
    assert taxon.is_accepted is True
    assert taxon.guids == {"NCBI": "taxon:9606"}
    assert taxon.branch_length == 0.1
    assert taxon.confidence == 0.95


def test_str_representation(taxon):
    expected_str = "Homo sapiens (species)"
    assert str(taxon) == expected_str


def test_repr_representation(taxon):
    expected_repr = "Taxon(name='Homo sapiens', taxonomic_rank='species')"
    assert repr(taxon) == expected_repr


def test_inheritance(taxon):
    assert isinstance(taxon, Clade)


def test_custom_attributes(taxon):
    custom_attrs = ['common_name', 'taxonomic_rank', 'taxonomic_authority',
                    'taxonomic_code', 'is_accepted', 'guids']
    for attr in custom_attrs:
        assert hasattr(taxon, attr)


def test_clade_attributes(taxon):
    clade_attrs = ['branch_length', 'name', 'clades', 'confidence']
    for attr in clade_attrs:
        assert hasattr(taxon, attr)