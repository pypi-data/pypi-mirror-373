import os
import sys
from pathlib import Path
from typing import Any

from setuptools import setup
from setuptools.command.bdist_wheel import bdist_wheel
from setuptools.command.sdist import sdist
from setuptools.dist import Distribution

sys.path.append(".")
import fetch

MM_SHA = os.environ.get("MM_SHA", "main").lower()
VERSION_FILE = Path("src/mm_test_adapters/version.py")


def write_version() -> str:
    version = fetch.fetch_sources(sha=MM_SHA)
    sha = fetch.get_sha()
    VERSION_FILE.write_text(
        f'__version__ = "{version}"\n'
        f'GIT_REF = "{sha}"\n'
        f'URL = "{fetch.DEFAULT_REPO}/tree/{sha}"'
    )
    return version


def get_version():
    if VERSION_FILE.exists():
        version_text = VERSION_FILE.read_text().strip().split("\n")[0]
        return version_text.split(" = ")[1].strip('"')
    else:
        try:
            return write_version()
        except Exception:
            return "0.0.0"


class CustomSdist(sdist):
    def run(self):
        write_version()
        super().run()


class CustomBdistWheel(bdist_wheel):
    def get_tag(self):
        # Force Python-version agnostic wheels: py3-none-<platform>
        _py, _abi, plat_tag = super().get_tag()
        return "py3", "none", plat_tag

    def write_wheelfile(self, wheelfile_base: str, **kwargs: Any) -> None:
        lib_dir = os.path.join(str(self.bdist_dir), "mm_test_adapters", "libs")
        fetch.build_libs(lib_dir)
        super().write_wheelfile(wheelfile_base, **kwargs)


class BinaryDistribution(Distribution):
    def has_ext_modules(self) -> bool:
        return True  # Forces a platform-specific wheel


setup(
    version=get_version(),
    cmdclass={"sdist": CustomSdist, "bdist_wheel": CustomBdistWheel},
    package_data={"*": ["*"]},
    package_dir={"": "src"},
    packages=["mm_test_adapters"],
    distclass=BinaryDistribution,
)
