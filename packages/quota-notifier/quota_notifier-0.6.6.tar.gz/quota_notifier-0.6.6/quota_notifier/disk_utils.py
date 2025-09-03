"""Utilities for fetching disk quota information.

Different quota objects (classes) are provided for different file system structures.
The ``GenericQuota`` is generally applicable to any file system whose
quota can be determined using the ``df`` commandline utility.

Quota classes may provide factory methods to facilitate creating instances
based on simple user data. In all cases, these methods will return ``None``
if a quota is not found for the user.

Using ``QuotaFactory`` class is recommended when dynamically creating quota
objects for varying paths, users, or filesystem types.

Module Contents
---------------
"""

from __future__ import annotations

import json
import logging
import math
from abc import abstractmethod
from copy import copy
from enum import Enum
from pathlib import Path
from typing import Iterable, Optional

from .settings import ApplicationSettings
from .shell import ShellCmd, User


class AbstractQuota(object):
    """Base class for building object-oriented representations of file system quotas."""

    def __init__(self, name: str, path: Path, user: User, size_used: int, size_limit: int) -> None:
        """Create a new quota from known system metrics

        Args:
            name: Human readable name of the file system
            path: Mounted file system path
            user: User that the quota is tied to
            size_used: Disk space used by the user/group
            size_limit: Maximum disk space allowed by the allocation

        Raises:
            ValueError: For a blank/empty ``name`` argument
        """

        if not name.strip():
            raise ValueError('Quota names cannot be blank')

        self.name = name
        self.user = user
        self.path = path
        self.size_used = size_used
        self.size_limit = size_limit

    @property
    def percentage(self) -> int:
        """Return the current quota utilization as an integer percentage"""

        return (self.size_used * 100) // self.size_limit

    @classmethod
    @abstractmethod
    def get_quota(cls, name: str, path: Path, user: User) -> Optional[AbstractQuota]:
        """Return a quota object for a given user and file path

        Args:
            name: Name of the file system
            path: The file path for create a quota for
            user: User that the quota is tied to

        Returns:
            An instance of the parent class or None if the allocation does not exist
        """

    @staticmethod
    def bytes_to_str(size: int) -> str:
        """Convert the given number of bytes to a human-readable string

        Args:
            size: An integer number of bytes

        Returns:
             A string representation of the given size with units
        """

        if size == 0:
            return '0.0 B'

        size_units = ('B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB')

        base_2_power = int(math.floor(math.log(size, 1024)))
        conversion_factor = math.pow(1024, base_2_power)
        final_size = round(size / conversion_factor, 2)
        return f'{final_size} {size_units[base_2_power]}'

    def __str__(self) -> str:
        """A human-readable string indicating the file system name and usage percentage"""

        used_str = self.bytes_to_str(self.size_used)
        limit_str = self.bytes_to_str(self.size_limit)
        return f"{self.name}: {used_str} / {limit_str} ({self.percentage}%)"


class GenericQuota(AbstractQuota):
    """The default quota object for most file system types"""

    @classmethod
    def get_quota(cls, name: str, path: Path, user: User) -> Optional[GenericQuota]:
        """Return a quota object for a given user and file path

        Args:
            name: Name of the file system
            path: The file path for create a quota for
            user: User that the quota is tied to

        Returns:
            An instance of the parent class or None if the allocation does not exist

        Raises:
            RuntimeError: If something goes wrong communicating with the file system
        """

        logging.debug(f'fetching generic quota for {user.username} at {path}')
        if not path.exists():
            logging.debug(f'Could not file path: {path}')
            return None

        df_command = ShellCmd(f"df {path}")
        if df_command.err:
            logging.error(df_command.err)
            return None

        result = df_command.out.splitlines()[1].split()
        quota = cls(name, path, user, int(result[2]) * 1024, int(result[1]) * 1024)
        logging.debug(str(quota))
        return quota


class BeeGFSQuota(AbstractQuota):
    """Disk storage quota for a BeeGFS file system"""

    # Map file system path to cached quota objects {file path: {group ID: quota object}}
    _cached_quotas: dict[Path: dict[int: BeeGFSQuota]] = dict()

    @classmethod
    def get_quota(cls, name: str, path: Path, user: User, storage_pool: int = 1) -> Optional[BeeGFSQuota]:
        """Return a quota object for a given user and file path

        Args:
            name: Name of the file system
            path: The mount location for the BeeGFS system
            user: User that the quota is tied to
            storage_pool: BeeGFS storagepoolid to create a quota for

        Returns:
            An instance of the parent class or None if the allocation does not exist

        Raises:
            FileNotFoundError: If the given file path does not exist
            RuntimeError: If something goes wrong communicating with the file system
        """

        logging.debug(f'fetching BeeGFS quota for {user.username} at {path}')
        if not path.exists():
            logging.debug(f'Could not file path: {path}')
            return None

        cached_quota = cls._cached_quotas.get(path, dict()).get(user.gid, None)
        if cached_quota:
            logging.debug(f'Found cached quota for {user.gid} under {path}')
            quota = copy(cached_quota)
            quota.user = user

        else:
            logging.debug(f'No cached quota for {user.gid} under {path}')
            bgfs_command = f"beegfs-ctl --getquota --csv --mount={path} --storagepoolid={storage_pool} --gid {user.gid}"
            quota_info_cmd = ShellCmd(bgfs_command)
            if quota_info_cmd.err:
                logging.error(quota_info_cmd.err)
                return None

            result = quota_info_cmd.out.splitlines()[1].split(',')
            quota = cls(name, path, user, int(result[2]), int(result[3]))

        logging.debug(str(quota))
        return quota

    @classmethod
    def cache_quotas(cls, name: str, path: Path, users: Iterable[User], storage_pool: int = 1) -> None:
        """Cache quota information for multiple users

        Fetch and cache quota information for multiple users with a bulk
        BeeGFS query. Cached information is used to speed up future calls to
        the ``get_quota`` method.

        Args:
            name: Name of the file system
            path: The mount location for the BeeGFS system
            users: List of users to query for
            storage_pool: BeeGFS storagepoolid to create a quota for

        Yield:
            Quota objects for each user having a quota
        """

        logging.info(f'Caching quota information for path {path}')

        group_ids = ','.join(map(str, set(user.gid for user in users)))  # CSV string of unique group IDs
        cmd_str = f"beegfs-ctl --getquota  --csv --mount={path} --storagepoolid={storage_pool} --gid --list {group_ids}"

        # Fetch quota data from BeeGFS via the underlying shell
        quota_info_cmd = ShellCmd(cmd_str, timeout=60 * 5)
        if quota_info_cmd.err:
            logging.error(quota_info_cmd.err)
            raise RuntimeError(quota_info_cmd.err)

        # Cache returned values for future use
        cls._cached_quotas[path] = dict()
        for quota_data in quota_info_cmd.out.splitlines()[1:]:
            _, gid, used, avail, *_ = quota_data.split(',')
            cls._cached_quotas[path][int(gid)] = cls(name, path, None, int(used), int(avail))


class IhomeQuota(AbstractQuota):
    """Disk storage quota for the ihome file system"""

    _parsed_quota_data = None

    @classmethod
    def _get_quota_data(cls) -> dict:
        """Parse and cache Ihome quota data

        Returns:
            Quota information as a dictionary
        """

        # Get the information from Isilon
        if cls._parsed_quota_data is None:
            ihome_data_path = ApplicationSettings.get('ihome_quota_path')
            logging.debug(f'Parsing {ihome_data_path}')
            with ihome_data_path.open('r') as infile:
                cls._parsed_quota_data = json.load(infile)

        return cls._parsed_quota_data

    @classmethod
    def get_quota(cls, name: str, path: Path, user: User) -> Optional[IhomeQuota]:
        """Return a quota object for a given user and file path

        Args:
            name: Name of the file system
            path: The file path for create a quota for
            user: User that the quota is tied to

        Returns:
            An instance of the parent class or None if the allocation does not exist
        """

        logging.debug(f'fetching Ihome quota for {user.username} at {path}')

        quota_data = cls._get_quota_data()
        persona = f"UID:{user.uid}"
        for item in quota_data["quotas"]:
            if item["persona"] is not None:
                if item["persona"]["id"] == persona:
                    quota = cls(name, path, user, item["usage"]["logical"], item["thresholds"]["hard"])
                    logging.debug(str(quota))
                    return quota


class QuotaFactory:
    """Factory object for dynamically creating quota instances of different types"""

    class QuotaType(Enum):
        """Map file system types to quota objects"""

        # When modifying these options, also update the options accepted by the settings schema
        # settings.FileSystemSchema.type
        generic = GenericQuota
        beegfs = BeeGFSQuota
        ihome = IhomeQuota

    def __new__(cls, quota_type: str, name: str, path: Path, user: User, **kwargs) -> AbstractQuota:
        """Create a new quota instance

        See the ``QuotaType`` attribute for valid values to the ``quota_type`` argument.

        Args:
            quota_type: String representation of the return type object
            name: Name of the file system
            path: The file path for create a quota for
            user: User that the quota is tied to

        Return:
              A quota instance of the specified type created using the given arguments
        """

        try:
            quota_class = cls.QuotaType[quota_type].value

        except KeyError:
            logging.error(f'Could not create quota object ')
            raise ValueError(f'Unknown quota type quota_type: {quota_type}, path: {path}, user: {user}')

        return quota_class.get_quota(name, path, user, **kwargs)
