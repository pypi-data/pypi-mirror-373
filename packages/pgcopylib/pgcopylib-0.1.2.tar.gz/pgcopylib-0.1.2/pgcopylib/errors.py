class PGCopyError(Exception):
    """Base PGCopy error."""


class PGCopyEOFError(PGCopyError):
    """PGCopy end of file error."""


class PGCopySignatureError(ValueError):
    """Signature not match."""


class PGCopyRecordError(ValueError):
    """Record length error."""


class PGCopyOidNotSupportError(ValueError):
    """Oid not support error."""
