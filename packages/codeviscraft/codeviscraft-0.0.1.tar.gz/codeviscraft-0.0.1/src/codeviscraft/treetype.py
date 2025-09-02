from enum import Enum
class TreeType(str, Enum):
    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))

    def __str__(self):
        return str.__str__(self)
    ACACIA = "ACACIA"
    AZALEA = "AZALEA"
    BIG_TREE = "BIG_TREE"
    BIRCH = "BIRCH"
    MROWN_MUSHROOM = "MROWN_MUSHROOM"
    CHERRY = "CHERRY"
    CHORUS_PLANT = "CHORUS_PLANT"
    COCOA_TREE = "COCOA_TREE"
    CRIMSON_FUNGUS = "CRIMSON_FUNGUS"
    DARK_OAK = "DARK_OAK"
    JUNGLE = "JUNGLE"
    JUNGLE_BUSH = "JUNGLE_BUSH"
    MANGROVE = "MANGROVE"
    MEGA_PINE = "MEGA_PINE"
    MEGA_REDWOOD = "MEGA_REDWOOD"
    REDWOOD = "REDWOOD"
    SMALL_JUNGLE = "SMALL_JUNGLE"
    SWAMP = "SWAMP"
    TALL_BIRCH = "TALL_BIRCH"
    TALL_REDWOOD = "TALL_REDWOOD"
    TREE = "TREE"
    WARPED_FUNGUS = "WARPED_FUNGUS"
