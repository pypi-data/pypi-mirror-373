"""Handling of user notifications and notification history.

The ``notify`` module provides logic for checking if users have pending
notifications and issuing those notifications via email.

Module Contents
---------------
"""

import logging
from bisect import bisect_right
from email.message import EmailMessage
from pathlib import Path
from smtplib import SMTP
from typing import Collection, Optional, Set, Union, Tuple, List
from typing import Iterable

from sqlalchemy import delete, insert, select
from sqlalchemy.orm import Session

from .disk_utils import AbstractQuota, BeeGFSQuota, QuotaFactory
from .orm import DBConnection, Notification
from .settings import ApplicationSettings
from .shell import User

DEFAULT_TEMPLATE_PATH = Path(__file__).parent / 'data' / 'template.html'
CUSTOM_TEMPLATE_PATH = Path('/etc/notifier/template.html')


class EmailTemplate:
    """A formattable email template to notify users about their disk quota usage"""

    email_subject = ApplicationSettings.get('email_subject')
    email_from = ApplicationSettings.get('email_from')

    if CUSTOM_TEMPLATE_PATH.exists():
        email_template = CUSTOM_TEMPLATE_PATH.read_text()

    else:
        email_template = DEFAULT_TEMPLATE_PATH.read_text()

    def __init__(self, quotas: Collection[AbstractQuota]) -> None:
        """Generate a formatted instance of the email template

        Args:
            quotas: Disk quotas to mention in the email
        """

        quota_str = r'<br>'.join(map(str, quotas))
        self.message = self.email_template.format(usage_summary=quota_str)

    def send_to_user(self, user: User, smtp: Optional[SMTP] = None) -> EmailMessage:
        """Send the formatted email to the given username

        Args:
            user: Name of the user to send to
            smtp: Optionally use a custom SMTP server
        """

        domain = ApplicationSettings.get('email_domain').lstrip('@')
        return self.send(address=f'{user.username}@{domain}', smtp=smtp)

    def send(self, address: str, smtp: Optional[SMTP] = None) -> EmailMessage:
        """Send the formatted email to the given email address

        The default smtp server is determined via the current application settings.

        Args:
            address: Destination email address
            smtp: Optionally use a custom SMTP server
        """

        email = EmailMessage()
        email.set_content(self.message, subtype='html')
        email["Subject"] = self.email_subject
        email["From"] = self.email_from
        email["To"] = address

        logging.debug(f'Sending email notification to {address}')
        if ApplicationSettings.get('debug'):
            return email

        with smtp or SMTP(
            host=ApplicationSettings.get('smtp_host'),
            port=ApplicationSettings.get('smtp_port')
        ) as smtp_server:
            smtp_server.send_message(email)

        return email


class UserNotifier:
    """Issue and manage user quota notifications"""

    @classmethod
    def get_users(cls) -> Iterable[User]:
        """Return a collection of users to check quotas for

        Returns:
            An iterable collection of ``User`` objects
        """

        logging.info('Fetching user list...')
        uid_blacklist = ApplicationSettings.get('uid_blacklist')
        gid_blacklist = ApplicationSettings.get('gid_blacklist')

        allowed_users = []
        for user in User.iter_all_users():
            if not (cls._id_in_blacklist(user.uid, uid_blacklist) or cls._id_in_blacklist(user.gid, gid_blacklist)):
                allowed_users.append(user)

        logging.debug(f'Found {len(allowed_users)} non-blacklisted users')
        return allowed_users

    @staticmethod
    def _id_in_blacklist(id_value: int, blacklist: Set[Union[int, Tuple[int, int]]]) -> bool:
        """Return whether an ID is in a black list of ID values

        Args:
            id_value: The ID value to check
            blacklist: A collection of ID values and ID ranges

        Returns:
            Whether the ID is in the blacklist
        """

        for id_def in blacklist:
            if isinstance(id_def, int) and id_value == id_def:
                return True

            elif isinstance(id_def, tuple) and (id_def[0] <= id_value <= id_def[1]):
                return True

        return False

    @staticmethod
    def get_user_quotas(user: User) -> List[AbstractQuota]:
        """Return a tuple of quotas assigned to a given user

        Args:
            user: The user to fetch quotas for

        Returns:
            An iterable collection of quota objects
        """

        quota_list = []
        for file_sys in ApplicationSettings.get('file_systems'):
            user_path = file_sys.path
            if file_sys.type == 'generic':
                user_path /= user.group

            quota = QuotaFactory(quota_type=file_sys.type, name=file_sys.name, path=user_path, user=user)
            if quota:
                quota_list.append(quota)

        return quota_list

    @staticmethod
    def get_last_threshold(session: Session, quota: AbstractQuota) -> Optional[int]:
        """Return the last threshold a user was notified for

        If no previous notification history can be found, the return value is None

        Args:
            session: Active database session for performing select queries
            quota: The quota to get a threshold for

        Returns:
            The last notification or None if there was no notification
        """

        query = select(Notification).where(
            Notification.username == quota.user.username,
            Notification.file_system == quota.name)

        last_notification = None
        db_entry = session.execute(query).scalars().first()
        if db_entry:
            last_notification = db_entry.threshold

        return last_notification

    @staticmethod
    def get_next_threshold(quota: AbstractQuota) -> Optional[int]:
        """Return the next threshold a user should be notified for

        The return value will be less than or equal to the current quota usage.
        If there is no notification threshold less than the current usage, the return value is None.

        Args:
            quota: The quota to get a threshold for

        Returns:
            The largest notification threshold that is less than the current usage or None
        """

        # Get the notification thresholds for the given file system quota
        file_systems = ApplicationSettings.get('file_systems')
        thresholds = next(fs.thresholds for fs in file_systems if fs.name == quota.name)

        next_threshold = None
        if quota.percentage >= min(thresholds):
            index = bisect_right(thresholds, quota.percentage)
            next_threshold = thresholds[index - 1]

        return next_threshold

    def notify_user(self, user: User) -> None:
        """Send any pending email notifications the given user

        Args:
            user: The user to send a notification to
        """

        logging.debug(f'Checking quotas for {user}...')

        notify_user = False
        with DBConnection.session() as session:
            quota_list = self.get_user_quotas(user)
            for quota in quota_list:
                next_threshold = self.get_next_threshold(quota)
                last_threshold = self.get_last_threshold(session, quota)

                # Usage is below the lowest threshold
                # Clean up the DB and continue
                if next_threshold is None:
                    session.execute(
                        delete(Notification).where(
                            Notification.username == user.username,
                            Notification.file_system == quota.name
                        )
                    )

                # There was no previous notification
                # Mark the quota as needing a notification and create a DB record
                elif last_threshold is None or next_threshold > last_threshold:
                    notify_user = True
                    session.execute(
                        insert(Notification).values(
                            username=user.username,
                            file_system=quota.name,
                            threshold=next_threshold
                        )
                    )

                # Quota usage dropped to a lower threshold
                # Update the DB and do not issue a notification
                elif next_threshold <= last_threshold:
                    session.execute(
                        insert(Notification).values(
                            username=user.username,
                            file_system=quota.name,
                            threshold=next_threshold
                        )
                    )

            # Issue email notification if necessary
            if notify_user:
                logging.info(f'{user} has one or more quotas pending notification')
                EmailTemplate(quota_list).send_to_user(user)

            else:
                logging.debug(f'{user} has no quotas pending notification')

            # Wait to commit until the email sends
            session.commit()

    def send_notifications(self) -> None:
        """Send email notifications to any users who have exceeded a notification threshold"""

        users = self.get_users()

        # Cache queries for BeeGFS file systems
        logging.info('Checking for cachable file system queries...')
        cachable_systems_found = False

        for file_system in ApplicationSettings.get('file_systems'):
            if file_system.type == 'beegfs':
                cachable_systems_found = True
                BeeGFSQuota.cache_quotas(name=file_system.name, path=file_system.path, users=users)

        if not cachable_systems_found:
            logging.debug('No cachable system queries found')

        logging.info('Scanning user quotas...')
        failure = False
        for user in users:
            try:
                self.notify_user(user)

            except Exception as caught:
                # Only include exception information in the logfile, not the console
                logging.getLogger('file_logger').error(f'Error notifying {user}', exc_info=caught)
                logging.getLogger('console_logger').error(f'Error notifying {user} - {caught}')
                failure = True

        if failure and ApplicationSettings.get('admin_emails'):
            logging.getLogger('smtp_logger').critical(
                'Email notifications failed for one or more user accounts. See the application logs for more details.'
            )
