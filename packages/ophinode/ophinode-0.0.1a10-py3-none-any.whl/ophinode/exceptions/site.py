class InvalidConfigurationError(Exception):
    pass

class RootPathUndefinedError(InvalidConfigurationError):
    pass

class RootPathIsNotADirectoryError(InvalidConfigurationError):
    pass

class NoCurrentPageError(Exception):
    pass

class ExportPathCollisionError(Exception):
    pass
