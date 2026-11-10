from setuptools import setup
import os
from codecs import open

_here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(_here, "README.rst")) as f:
    long_description = f.read()

packages = ["KonoPyUtil", "KonoPyUtil/soccer", "KonoPyUtil/other"]

install_requires = [
    "pandas==3.1.1",
    "SQLAlchemy==2.1.8",
    "environs==15.2.0",
    "psycopg2-binary==2.9.13",
    "ipinfo==5.6.0",
    "requests==2.34.2",
    "openpyxl==3.1.5",
]

about = {}
with open(os.path.join(_here, "KonoPyUtil", "__version__.py"), "r", "utf-8") as f:
    exec(f.read(), about)

setup(
    name=about["__title__"],
    version=about["__version__"],
    description=about["__description__"],
    long_description=long_description,
    long_description_content_type="text/x-rst",
    author=about["__author__"],
    author_email=about["__author_email__"],
    url=about["__url__"],
    packages=packages,
    package_dir={"KonoPyUtil": "KonoPyUtil"},
    package_data={"KonoPyUtil": ["data/*"]},
    include_package_data=True,
    python_requires=">=3.13",
    install_requires=install_requires,
    extras_require={"test": ["pytest"]},
    license=about["__license__"],
    project_urls={
        "Source": "https://github.com/konoanalytics/KonoPyUtil",
    },
)
