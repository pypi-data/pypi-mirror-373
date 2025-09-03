import tarfile
from Bio.Phylo import BaseTree
from nbitk.Taxon import Taxon
import logging
from collections import defaultdict


class Parser:
    def __init__(self, file):
        self.file = file

    def _parse_nodes_dmp(self, nodes_file):
        """Parse nodes.dmp file to build adjacency list and node metadata."""
        nodes = {}
        children = defaultdict(list)

        for line in nodes_file:
            line = line.decode('utf-8').strip()
            if not line:
                continue

            parts = [part.strip() for part in line.split('\t|\t')]
            if len(parts) < 3:
                continue

            tax_id = parts[0]
            parent_tax_id = parts[1]
            rank = parts[2]

            nodes[tax_id] = {
                'parent': parent_tax_id,
                'rank': rank,
                'tax_id': tax_id
            }

            # Build adjacency list (parent -> children)
            if tax_id != parent_tax_id:  # Skip root node self-reference
                children[parent_tax_id].append(tax_id)

        return nodes, children

    def _parse_names_dmp(self, names_file):
        """Parse names.dmp file to get scientific names."""
        names = {}
        line_count = 0

        for line in names_file:
            line = line.decode('utf-8').strip()
            line_count += 1
            if not line:
                continue

            # Split by tab-pipe-tab, but handle the trailing pipe
            parts = line.split('\t|\t')
            if len(parts) < 4:
                continue

            # Remove trailing '|' from the last part if present
            parts = [part.strip().rstrip('|').strip() for part in parts]

            tax_id = parts[0]
            name = parts[1]
            name_class = parts[3]

            # We want the scientific name
            if name_class == 'scientific name':
                names[tax_id] = name

        logger = logging.getLogger(__name__)
        logger.debug(f"Parsed {len(names)} names from {line_count} lines in names.dmp")

        return names

    def _build_taxon_tree(self, nodes, names, children, tax_id):
        """Recursively build Taxon tree from parsed data."""
        node_data = nodes[tax_id]
        name = names.get(tax_id, f"Unknown_{tax_id}")
        rank = node_data['rank']

        # Create Taxon object with same structure as original
        taxon = Taxon(
            name=name,
            taxonomic_rank=rank,
            guids={"taxon": tax_id}
        )

        # Recursively add children
        for child_tax_id in children.get(tax_id, []):
            child_taxon = self._build_taxon_tree(nodes, names, children, child_tax_id)
            taxon.clades.append(child_taxon)

        return taxon

    def parse(self):
        """Parse NCBI taxonomy dump and return BaseTree.Tree with Taxon objects."""
        logger = logging.getLogger(__name__)

        logger.debug("Loading NCBI taxonomy dump...")

        # Handle both file paths and already-opened TarFile objects
        if isinstance(self.file, tarfile.TarFile):
            tar = self.file
            should_close = False
        else:
            tar = tarfile.open(self.file, 'r:gz')
            should_close = True

        try:
            # Extract nodes.dmp
            nodes_member = tar.getmember('nodes.dmp')
            nodes_file = tar.extractfile(nodes_member)

            logger.debug("Parsing nodes.dmp...")
            nodes, children = self._parse_nodes_dmp(nodes_file)

            # Extract names.dmp
            names_member = tar.getmember('names.dmp')
            names_file = tar.extractfile(names_member)

            logger.debug("Parsing names.dmp...")
            names = self._parse_names_dmp(names_file)

            logger.debug("Building taxonomy tree...")

            # Find root node (where tax_id == parent_tax_id)
            root_tax_id = None
            for tax_id, node_data in nodes.items():
                if tax_id == node_data['parent']:
                    root_tax_id = tax_id
                    break

            if root_tax_id is None:
                raise ValueError("Could not find root node in taxonomy")

            # Build tree starting from root
            root_taxon = self._build_taxon_tree(nodes, names, children, root_tax_id)

            # Create BaseTree
            bt = BaseTree.Tree(root_taxon)

            logger.debug(f"Successfully loaded taxonomy with {len(nodes)} nodes")

        finally:
            # Only close if we opened it
            if should_close:
                tar.close()

        return bt