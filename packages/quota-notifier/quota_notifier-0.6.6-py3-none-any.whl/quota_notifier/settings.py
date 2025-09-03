"""Application settings management.

Class definitions inheriting from ``BaseSettings`` directly define
the settings file schema.  The ``ApplicationSettings`` class is used to manage
application settings in memory.

Module Contents
---------------
"""

import logging
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any, List, Literal, Optional, Set, Tuple, Union

from pydantic import field_validator, Field
from pydantic_settings import BaseSettings

DEFAULT_DB_PATH = Path.cwd().resolve() / 'notifier_data.db'


class FileSystemSchema(BaseSettings):
    """Defines the schema settings related to an individual file system"""

    name: str = Field(
        ...,
        title='System Name',
        description='Human readable name for the file system')

    path: Path = Field(
        ...,
        title='System Path',
        description='Absolute path to the mounted file system')

    # If modifying options for this setting, also update
    # quota_notifier.disk_utils.QuotaFactory.QuotaType
    type: Literal['ihome', 'generic', 'beegfs'] = Field(
        ...,
        title='System Type',
        description='Type of the file system')

    thresholds: List[int] = Field(
        title='Notification Thresholds',
        description='Usage percentages to issue notifications for.')

    @field_validator('name')
    @classmethod
    def validate_name(cls, value: str) -> str:
        """Ensure the given name is not blank

        Args:
            value: The name value to validate

        Returns:
            The validated file system name
        """

        stripped = value.strip()
        if not stripped:
            raise ValueError(f'File system name cannot be blank')

        return stripped

    @field_validator('path')
    @classmethod
    def validate_path(cls, value: Path) -> Path:
        """Ensure the given system path exists

        Args:
            value: The path value to validate

        Returns:
            The validated path object

        Raises:
            ValueError: If the path does not exist
        """

        if not value.exists():
            raise ValueError(f'File system path does not exist {value}')

        return value

    @field_validator('thresholds')
    @classmethod
    def validate_thresholds(cls, value: list) -> list:
        """Validate threshold values are between 0 and 100 (exclusive)

        Args:
            value: List of threshold values to validate

        Returns:
            The validated threshold values
        """

        if not value:
            raise ValueError(f'At least one threshold must be specified per file system')

        for threshold in value:
            if not 100 > threshold > 0:
                raise ValueError(f'Notification threshold {threshold} must be greater than 0 and less than 100')

        return value


class SettingsSchema(BaseSettings):
    """Defines the schema and default values for top level application settings"""

    # General application settings
    ihome_quota_path: Path = Field(
        title='Ihome Quota Path',
        default=Path('/ihome/crc/scripts/ihome_quota.json'),
        description='Path to ihome storage information.')

    file_systems: List[FileSystemSchema] = Field(
        title='Monitored File Systems',
        default=list(),
        description='List of additional settings that define which file systems to examine.')

    uid_blacklist: Set[Union[int, Tuple[int, int]]] = Field(
        title='Blacklisted User IDs',
        default=[0],
        description='Do not notify users with these ID values.')

    gid_blacklist: Set[Union[int, Tuple[int, int]]] = Field(
        title='Blacklisted Group IDs',
        default=[0],
        description='Do not notify groups with these ID values.')

    disk_timeout: int = Field(
        title='File System Timeout',
        default=30,
        description='Give up on checking a file system after the given number of seconds.')

    # Settings for application logging
    log_level: Literal['DEBUG', 'INFO', 'WARNING', 'ERROR'] = Field(
        title='Logging Level',
        default='INFO',
        description='Application logging level.')

    log_path: Optional[Path] = Field(
        title='Log Path',
        default_factory=lambda: Path(NamedTemporaryFile().name),
        description='Optionally log application events to a file.')

    # Settings for the smtp host/port
    smtp_host: str = Field(
        title='SMTP Server Host Name',
        default='',
        description='Name of the SMTP host server'
    )

    smtp_port: int = Field(
        title='SMTP Port Number',
        default=0,
        description='Port for the SMTP server'
    )

    # Settings for database connections
    db_url: str = Field(
        title='Database Path',
        default=f'sqlite:///{DEFAULT_DB_PATH}',
        description=('URL for the application database. '
                     'By default, a SQLITE database is created in the working directory.'))

    # Email notification settings
    email_from: str = Field(
        title='Email From Address',
        default='no-reply@domain.com',
        description='From address for automatically generated emails.')

    email_subject: str = Field(
        title='Email Subject Line',
        default='CRC Disk Usage Alert',
        description='Subject line for automatically generated emails.')

    email_domain: str = Field(
        title='User Email Address Domain',
        default='@domain.com',
        description=('String to append to usernames when generating user email addresses. '
                     'The leading `@` is optional.'))

    admin_emails: List[str] = Field(
        title='Administrator Emails',
        default=[],
        description='Admin users to contact when the application encounters a critical issue.'
    )

    # Settings for debug / dry-runs
    debug: bool = Field(
        title='Debug Mode',
        default=False,
        description='Disable database commits and email notifications. Useful for development and testing.')

    @field_validator('file_systems')
    @classmethod
    def validate_unique_file_systems(cls, value: List[FileSystemSchema]) -> List[FileSystemSchema]:
        """Ensure file systems have unique names/paths

        Args:
            value: The file systems to validate

        Returns:
            The validated file systems

        Raises:
            ValueError: If the file system names and paths are not unique
        """

        paths = [fs.path for fs in value]
        if len(set(paths)) != len(paths):
            raise ValueError('File systems do not have unique paths')

        names = [fs.name for fs in value]
        if len(set(names)) != len(names):
            raise ValueError('File systems do not have unique names')

        return value


class ApplicationSettings:
    """Configurable application settings object

    Use the ``configure`` method to override individual default settings.
    Use the ``configure_from_file`` method to load settings from a settings file.
    """

    _parsed_settings: SettingsSchema = SettingsSchema()

    @classmethod
    def set_from_file(cls, path: Path) -> None:
        """Reset application settings to default values

        Values defined in the given file path are used to override defaults.

        Args:
            path: Path to load settings from
        """

        cls._parsed_settings = SettingsSchema.model_validate_json(path.read_text())

    @classmethod
    def set(cls, **kwargs) -> None:
        """Update values in the application settings

        Unlike the ``configure`` and ``configure_from_file`` methods,
        application settings not specified as keyword arguments are left
        unchanged.

        Raises:
            ValueError: If the item name is not a valid setting
        """

        for item, value in kwargs.items():
            if not hasattr(cls._parsed_settings, item):
                ValueError(f'Invalid settings option: {item}')

            setattr(cls._parsed_settings, item, value)

    @classmethod
    def reset_defaults(cls) -> None:
        """Reset application settings to default values"""

        logging.debug('Resetting application settings to defaults')
        cls._parsed_settings = SettingsSchema()

    @classmethod
    def get(cls, item: str) -> Any:
        """Return a value from application settings

        Valid arguments include any attribute name for the
        ``SettingsSchema`` class.

        Args:
            item: Name of the settings value to retrieve

        Returns
           The value currently configured in application settings
        """

        return getattr(cls._parsed_settings, item)
