"""A simple command line application for notifying users when their storage
quota exceeds a certain percentage.

Overview
--------

Multi-tenant computing environments commonly enforce user/group limits on
shared storage resources. Enforcing storage quotas ensures resources
are shared fairly among users and is often necessary for establishing
broader system policies. However, quota enforcement can also come as a
hindrance to users when not implemented in a clear, accessible way.

The Quota Notification Utility automatically scans attached file systems and
issues email notifications to users exceeding a certain percentage of their
storage quota. The tool is easily configurable and supports multiple file
system types and custom notification thresholds.

How it Works
------------

The Quota Notification Utility automatically iterates through all users listed
in the local SSSD and all filesystems listed in the application settings file.
If a user has met or exceeded a configurable percentage for any of their storage
quotas, they are issued an email detailing their current usage.

Email notifications are only issued once per filesystem/threshold combination.
However, a user will receive additional notifications if their usage drops below
a threshold before exceeding the threshold a second time.
"""

import importlib.metadata

try:
    __version__ = importlib.metadata.version('quota-notifier')

except importlib.metadata.PackageNotFoundError:  # pragma: no cover
    __version__ = '0.0.0'
