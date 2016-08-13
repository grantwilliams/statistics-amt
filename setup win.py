from distutils.core import setup
import py2exe

PACKAGES = ['bs4', 'mechanicalsoup', 'PIL', 'psutil', 'requests', 'selenium', 'wheel']
MODULES = ['calculate_statistics.py', 'combobox_dicts.py', 'country_dicts.py', 'display_results.py', 'hostelworld.py',
           'myallocator.py', 'sa_options.py', 'statistic_amt.py']
DATA_FILES = ['.data_files', '.images', '.icons', '.phantomjs']
setup(
    name="Statistik Rechner",
    date_files=DATA_FILES,
    options={
        "py2exe": {
            "unbuffered": True,
            "bundle_files": 1,
            "optimize": 2,
            # "includes": MODULES,
            "packages": PACKAGES
            }
    },
    zipfile=None,
    windows=[{
        "script": "main.py",
        "icon_resources": [(1, ".icons/statistik-rechner-bar-black.ico")]
    }],
)
