class OssDBException(Exception):
    """Base oss client exception that all others inherit."""


class OssDBMergeError(OssDBException):
    """
    Exception raised when execute merge operation fails.
    """


class OssDBPutPartError(OssDBException):
    """
    Exception raised when upload part operation fails.
    """


class OssDBPutObjError(OssDBException):
    """
    Exception raised when upload operation fails.
    """


class OssDBAppendObjError(OssDBException):
    """Exception raised when upload operation fails."""


class OssDBInitPartError(OssDBException):
    """Exception raised when init upload operation fails."""
