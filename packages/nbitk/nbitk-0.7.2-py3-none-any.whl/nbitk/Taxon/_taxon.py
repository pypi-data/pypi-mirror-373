from typing import Dict, Optional
from Bio.Phylo.BaseTree import Clade


class Taxon(Clade):
    def __init__(
        self,
        name: str,
        common_name: str = None,
        taxonomic_rank: str = None,
        taxonomic_authority: str = None,
        taxonomic_code: str = None,
        is_accepted: bool = False,
        guids: Dict[str, str] = None,
        branch_length: Optional[float] = None,
        clades: Optional[list] = None,
        confidence: Optional[float] = None,
        color: Optional[str] = None,
        width: Optional[float] = None,
    ):
        super().__init__(
            branch_length=branch_length,
            name=name,
            clades=clades,
            confidence=confidence,
            color=color,
            width=width,
        )
        self.common_name = common_name
        self.taxonomic_rank = taxonomic_rank
        self.taxonomic_authority = taxonomic_authority
        self.taxonomic_code = taxonomic_code
        self.is_accepted = is_accepted
        self.guids = guids if guids is not None else {}

    def __str__(self) -> str:
        return f"{self.name} ({self.taxonomic_rank})"

    def __repr__(self) -> str:
        return f"Taxon(name='{self.name}', taxonomic_rank='{self.taxonomic_rank}')"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Taxon):
            return NotImplemented
        # Compare based on name and taxonomic rank
        return self.name == other.name and self.taxonomic_rank == other.taxonomic_rank

    def __hash__(self):
        return hash((self.name, self.taxonomic_rank))

    @property
    def children(self):
        return self.clades
