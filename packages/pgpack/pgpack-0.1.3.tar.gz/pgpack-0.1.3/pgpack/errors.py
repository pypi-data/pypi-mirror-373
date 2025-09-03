class PGPackError(Exception):
    """Base PGPack error."""


class PGPackHeaderError(ValueError):
    """Error header signature."""


class PGPackMetadataCrcError(ValueError):
    """Error metadata crc32."""


class PGPackModeError(ValueError):
    """Error fileobject mode."""
