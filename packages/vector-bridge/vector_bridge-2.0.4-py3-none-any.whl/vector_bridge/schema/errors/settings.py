class SettingError(Exception):
    """Base class for Setting-related errors."""


def raise_for_setting_detail(detail: str) -> None:
    """
    Raises the corresponding SettingError based on the given setting error detail string.
    """
    raise SettingError(detail)
