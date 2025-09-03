"""The ``__main__.py`` file adds support for running the parent package as
a script via the ``python -m`` option.
"""

from .cli import Application

if __name__ == '__main__':
    Application.execute()
