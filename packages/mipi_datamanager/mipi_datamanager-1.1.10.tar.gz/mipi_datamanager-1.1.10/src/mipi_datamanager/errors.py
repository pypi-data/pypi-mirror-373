class ParameterError(Exception):
    "Error with parameters from a sql script"
    pass

class JinjaParameterError(ParameterError):
    "Error with jinja parameters from a sql script"
    pass

class FormatParameterError(ParameterError):
    """error with format parameters from a sql script"""
    pass

class ConfigError(Exception):
    """error with JinjaRepo config"""
    pass

class ConfigNotFoundError(ConfigError):
    """Can not find the config or the associated sql script"""
    pass

class InvalidConfigError(ConfigError):
    """Config is invalid due to incorrect formatting"""
    pass

class ConfigMismatchError(ConfigError):
    """Config is being used incorrectly likley a population information switch or key insert error"""
    pass


class InsertError(Exception):
    """Inserts not correctly entered into sql script"""
    pass

class GranularityError(Exception):
    """Raised when the granularity of a dataframe changes unexpectedly, usually due to a join"""

class MissingColumnError(KeyError):
    """Function expects the dataframe to have a specific column, but it is not found"""
