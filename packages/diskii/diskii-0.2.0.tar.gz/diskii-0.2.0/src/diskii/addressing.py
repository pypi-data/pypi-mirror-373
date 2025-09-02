"""Sector and block addressing utilities."""

from dataclasses import dataclass


@dataclass(frozen=True)
class SectorAddress:
    """Physical sector address (track, sector)."""

    track: int
    sector: int

    def __post_init__(self):
        if self.track < 0 or self.sector < 0:
            raise ValueError("Track and sector must be non-negative")

    def to_linear_sector(self, sectors_per_track: int) -> int:
        """Convert to linear sector number."""
        return self.track * sectors_per_track + self.sector

    @classmethod
    def from_linear_sector(
        cls, linear_sector: int, sectors_per_track: int
    ) -> "SectorAddress":
        """Create from linear sector number."""
        track = linear_sector // sectors_per_track
        sector = linear_sector % sectors_per_track
        return cls(track, sector)


@dataclass(frozen=True)
class BlockAddress:
    """Logical block address."""

    block: int

    def __post_init__(self):
        if self.block < 0:
            raise ValueError("Block number must be non-negative")

    def to_sector_addresses(
        self, sectors_per_track: int = 16
    ) -> tuple[SectorAddress, SectorAddress]:
        """Convert block to two sector addresses (ProDOS blocks are 512 bytes, sectors are 256)."""
        linear_sector = self.block * 2
        sector1 = SectorAddress.from_linear_sector(linear_sector, sectors_per_track)
        sector2 = SectorAddress.from_linear_sector(linear_sector + 1, sectors_per_track)
        return sector1, sector2

    @classmethod
    def from_sector_address(
        cls, sector: SectorAddress, sectors_per_track: int = 16
    ) -> "BlockAddress":
        """Create from sector address (uses first sector of block pair)."""
        linear_sector = sector.to_linear_sector(sectors_per_track)
        return cls(linear_sector // 2)


class AddressTranslator:
    """Translates between different addressing schemes."""

    def __init__(self, sectors_per_track: int = 16):
        self.sectors_per_track = sectors_per_track

    def sector_to_block(self, sector: SectorAddress) -> BlockAddress:
        """Convert sector address to block address."""
        return BlockAddress.from_sector_address(sector, self.sectors_per_track)

    def block_to_sectors(
        self, block: BlockAddress
    ) -> tuple[SectorAddress, SectorAddress]:
        """Convert block address to sector addresses."""
        return block.to_sector_addresses(self.sectors_per_track)

    def linear_to_sector(self, linear_sector: int) -> SectorAddress:
        """Convert linear sector number to track/sector."""
        return SectorAddress.from_linear_sector(linear_sector, self.sectors_per_track)

    def sector_to_linear(self, sector: SectorAddress) -> int:
        """Convert sector address to linear sector number."""
        return sector.to_linear_sector(self.sectors_per_track)


class DOSSectorInterleave:
    """Handle DOS 3.3 sector interleaving/skewing."""

    # DOS 3.3 sector skew table - maps logical to physical sectors
    DOS33_SKEW = [0, 7, 14, 6, 13, 5, 12, 4, 11, 3, 10, 2, 9, 1, 8, 15]

    @classmethod
    def logical_to_physical(cls, logical_sector: int) -> int:
        """Convert logical sector to physical sector using DOS 3.3 skew."""
        if 0 <= logical_sector < len(cls.DOS33_SKEW):
            return cls.DOS33_SKEW[logical_sector]
        return logical_sector

    @classmethod
    def physical_to_logical(cls, physical_sector: int) -> int:
        """Convert physical sector to logical sector using DOS 3.3 skew."""
        try:
            return cls.DOS33_SKEW.index(physical_sector)
        except ValueError:
            return physical_sector


class ProDOSBlockInterleave:
    """Handle ProDOS block to sector mapping."""

    # ProDOS sector skew - different from DOS 3.3
    PRODOS_SKEW = [0, 8, 1, 9, 2, 10, 3, 11, 4, 12, 5, 13, 6, 14, 7, 15]

    @classmethod
    def block_to_sectors(cls, block_num: int) -> tuple[int, int]:
        """Convert ProDOS block to two physical sectors."""
        logical_sector1 = block_num * 2
        logical_sector2 = block_num * 2 + 1

        # Apply sector skew
        physical_sector1 = cls.logical_to_physical(logical_sector1 % 16)
        physical_sector2 = cls.logical_to_physical(logical_sector2 % 16)

        return physical_sector1, physical_sector2

    @classmethod
    def logical_to_physical(cls, logical_sector: int) -> int:
        """Convert logical sector to physical sector using ProDOS skew."""
        if 0 <= logical_sector < len(cls.PRODOS_SKEW):
            return cls.PRODOS_SKEW[logical_sector]
        return logical_sector
