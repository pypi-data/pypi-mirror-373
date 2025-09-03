import sys
from distutils.core import setup

if not any(cmd in sys.argv for cmd in ["sdist", "egg_info"]):
    raise Exception(
        """
        Installation terminated!
        This is stub package to mitigate risks of Dependency Confusion attacks.
        As you install it - your configuration didn't configure properly.
        This is package not intended to be installed and highlight problems in your setup.
        
        Read more: https://jb.gg/dependency-confusion
        """
    )

setup()
