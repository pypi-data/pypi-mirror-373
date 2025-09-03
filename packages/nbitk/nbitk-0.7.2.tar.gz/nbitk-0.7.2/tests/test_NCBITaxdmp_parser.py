import pytest
import tempfile
import os
import requests
import tarfile
from nbitk.Phylo.NCBITaxdmp import Parser

@pytest.fixture
def ncbi_taxonomy_tar():
    # URL of the NCBI taxonomy dump
    url = "http://ftp.ncbi.nlm.nih.gov/pub/taxonomy/taxdump.tar.gz"

    # Create a temporary file
    with tempfile.NamedTemporaryFile(suffix=".tar.gz", delete=False) as temp_file:
        # Download the file
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Raise an exception for HTTP errors

        # Save the downloaded file
        for chunk in response.iter_content(chunk_size=8192):
            temp_file.write(chunk)

        # Get the path of the temporary file
        tar_path = temp_file.name

    # Open the tar file
    tar = tarfile.open(tar_path, "r:gz")

    # Yield the opened tar file
    yield tar

    # Clean up
    tar.close()
    os.unlink(tar_path)


def test_taxonomy_tree(ncbi_taxonomy_tar):
    parser = Parser(ncbi_taxonomy_tar)
    tree = parser.parse()

    # Check us
    we = list(tree.find_clades({'name': 'Homo sapiens'}))[0]
    assert we.guids['taxon'] == '9606'
    assert we.taxonomic_rank == 'species'
