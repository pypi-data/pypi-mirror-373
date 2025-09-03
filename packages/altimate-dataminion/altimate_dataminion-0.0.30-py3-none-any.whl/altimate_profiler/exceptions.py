class AltimateProfilerException(Exception):
    """
    Raised when the Altimate Profiler encounters an error.
    """

    pass


class AltimateDataStoreNotSupported(Exception):
    """
    Raised when the data store is not supported
    """

    pass


class AltimateDataStoreConnectionException(Exception):
    """
    Raised when the data store is not supported
    """

    pass


class AltimateInvalidInputException(Exception):
    pass


INVALID_UNICODE_IN_CSV = "Invalid unicode (byte sequence mismatch) detected in CSV file"


class AltimateInvalidCharactersInCSVException(Exception):
    pass
