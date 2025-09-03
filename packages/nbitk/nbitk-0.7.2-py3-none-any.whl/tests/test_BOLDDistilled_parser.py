import os
import pytest
import gzip
from nbitk.Phylo.BOLDDistilled import Parser

# Path to test files
@pytest.fixture
def tsv_handle():
    path = os.path.join(os.path.dirname(__file__), 'data', 'BOLDistilled_COI_Jul2025_TAXONOMY.tsv.gz')
    with gzip.open(path, 'rt') as f:  # 'rt' for text mode
        yield f

def test_BOLDDistilled_parser(tsv_handle):
    parser = Parser(tsv_handle)
    tree = parser.parse()
    assert tree.count_terminals() == 1061385, f"Expected 1061385 terminals, got {tree.count_terminals()}"
    assert tree.find_any(name="Barentsia gracilis").taxonomic_rank == 'species', f"Expected rank 'species'"