from distutils.core import setup
import py2exe


setup(
    options={
        "py2exe": {
            "unbuffered": True,
            "bundle_files": 1,
            "optimize": 2,
            "includes": ["sip"]
            }
    },
    zipfile=None,
    windows=[{
        "script": "wg_gesucht.py",
        "icon_resources": [(1, "apartment.ico")]
    }],
)
