import json
import os
import re
import shutil
import subprocess
import urllib.request
from pathlib import Path
from typing import Sequence

DEFAULT_DEVICES = ("DemoCamera", "Utilities", "NotificationTester", "SequenceTester")
DEFAULT_REPO = "https://github.com/micro-manager/mmCoreAndDevices"
DEFAULT_LIBDIR = "src/mm_test_adapters/libs"
DEFAULT_DEST = "src/mmCoreAndDevices"
DIV_RE = re.compile(r"#define DEVICE_INTERFACE_VERSION (\d+)")


def get_version(dest: str = DEFAULT_DEST) -> str:
    """Return version string, given a path to the mmCoreAndDevices folder.

    The version string is: DIV.YYYYMMDD with optional .postX suffix if
    versions already exist on PyPI for that date.
    """
    if not (Path(dest) / "MMDevice" / "MMDevice.h").exists():
        raise FileNotFoundError(
            f"Sources not found in {dest}. "
            "Please ensure the repository is cloned correctly."
        )
    match = DIV_RE.search((Path(dest) / "MMDevice" / "MMDevice.h").read_text())
    assert match, "Could not find DEVICE_INTERFACE_VERSION in MMDevice.h"

    _date = subprocess.check_output(
        ["git", "-C", dest, "log", "-1", "--format=%cd", "--date=format:'%Y%m%d'"]
    )
    date = _date.decode("utf-8").strip().replace("'", "")

    # Create base version
    version = f"{match.group(1)}.{date}"

    # Check PyPI for existing versions and determine post number
    if post_number := _get_next_pypi_post_version("mm-test-adapters", version):
        version += f".post{post_number}"
    return version


def _get_next_pypi_post_version(package_name: str, version_prefix: str) -> int:
    """Check PyPI for existing versions and return next `.postX` version.

    Args:
        package_name: The PyPI package name (e.g., 'mm-test-adapters')
        version_prefix: Version prefix to check (e.g., '71.20250825')
    """
    try:
        url = f"https://pypi.org/pypi/{package_name}/json"
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode())
        releases: dict[str, list[dict]] = data.get("releases", {})

        # Find all versions that start with our prefix
        matching_versions = [v for v in releases.keys() if v.startswith(version_prefix)]

        if not matching_versions:
            return 0

        # Extract post numbers from matching versions
        post_numbers = []
        for version in matching_versions:
            if version == version_prefix:
                post_numbers.append(0)  # Base version without .postX
            elif version.startswith(f"{version_prefix}.post"):
                try:
                    post_num = int(version.split(".post")[1])
                    post_numbers.append(post_num)
                except (IndexError, ValueError):
                    continue

        # Return the next post number
        return max(post_numbers) + 1 if post_numbers else 0

    except Exception:
        # If we can't reach PyPI or package doesn't exist, start with 0
        return 0


def get_sha(dest: str = DEFAULT_DEST) -> str:
    real_sha = subprocess.check_output(["git", "-C", dest, "rev-parse", "HEAD"])
    short_sha = real_sha.decode("utf-8").strip()[:7]
    return short_sha


def fix_library_names(lib_dir: str) -> None:
    """Fix names of *nix libraries in the specified directory.

    - For each file in the adapters directory:
      - If it ends with .dylib, rename to remove the extension
      - If it ends with .so, rename to end with .so.0
    """
    if not (adapters := Path(lib_dir)).exists():
        raise ValueError(f"Adapters directory does not exist: {adapters}")

    for entry in adapters.iterdir():
        if entry.is_file():
            name = entry.name
            if name.endswith(".dylib"):
                entry.rename(entry.with_suffix(""))
            elif name.endswith(".so"):
                entry.rename(entry.with_suffix(".so.0"))


def fetch_sources(
    repo: str = DEFAULT_REPO,
    sha: str = "main",
    devices: Sequence[str] = DEFAULT_DEVICES,
    dest: str = DEFAULT_DEST,
) -> str:
    """Clone `repo` into `dest`, checkout `sha`, and sparse-checkout `devices`."""
    if not os.path.exists(dest):
        subprocess.run(
            ["git", "clone", "--filter=blob:none", "--sparse", repo, dest],
            capture_output=True,
        )
    try:
        subprocess.run(
            ["git", "-C", dest, "checkout", sha], check=True, capture_output=True
        )
    except subprocess.CalledProcessError:
        raise ValueError(f"Failed to checkout SHA {sha!r}")

    subprocess.check_call(["git", "-C", dest, "sparse-checkout", "init", "--no-cone"])
    subprocess.check_call(
        ["git", "-C", dest, "sparse-checkout", "set", "/MMDevice/MMDevice.h"]
        + [f"DeviceAdapters/{device}" for device in devices]
    )
    return get_version(dest)


def build_libs(libdir: str = DEFAULT_LIBDIR) -> None:
    """Compile and install libraries into `libdir`.

    This runs the meson.build file in the root directory.  (NOTE: that file
    assumes that sources live in `src/mmCoreAndDevices`... so won't work if
    `fetch_sources` was used without `dest=src/mmCoreAndDevices`.
    """
    subprocess.check_call(
        [
            "meson",
            "setup",
            "builddir",
            "--vsenv",
            "--buildtype=release",
            "-Dmmdevice:tests=disabled",
            f"--libdir={libdir}",
            f"--bindir={libdir}",  # to also install the mmconfig_demo.cfg
        ]
    )
    subprocess.run(["meson", "compile", "-C", "builddir"])
    subprocess.run(["meson", "install", "--tags", "runtime", "-C", "builddir"])
    fix_library_names(libdir)


def main(
    repo: str = DEFAULT_REPO,
    sha: str = "main",
    devices: Sequence[str] = DEFAULT_DEVICES,
    dest: str = DEFAULT_DEST,
    build: bool = False,
    clean: bool = False,
    libdir: str = DEFAULT_LIBDIR,
) -> str:
    fetch_sources(repo, sha, devices, dest)
    version = get_version(dest)
    if build:
        build_libs(libdir)

    if clean:
        shutil.rmtree("builddir", ignore_errors=True)
        shutil.rmtree("include", ignore_errors=True)
        shutil.rmtree(dest, ignore_errors=True)

    return version


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--sha", default="main")
    parser.add_argument("--repo", default=DEFAULT_REPO)
    parser.add_argument("--libdir", default=DEFAULT_LIBDIR, help="Library directory")
    parser.add_argument("--build", action="store_true", help="Build the repository")
    parser.add_argument("--clean", action="store_true")
    args = parser.parse_args()

    version = main(
        repo=args.repo,
        sha=args.sha,
        build=args.build,
        clean=args.clean,
        libdir=args.libdir,
    )

    print(version)
