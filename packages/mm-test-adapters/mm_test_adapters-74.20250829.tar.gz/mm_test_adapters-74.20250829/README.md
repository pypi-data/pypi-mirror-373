# mm-test-adapters

This builds device adapters commonly used for testing and
development of mmCoreAndDevices (micro-manager).

- DemoCamera
- Utilities
- SequenceTester
- NotificationTester

It makes these builds available in two places:

1. Via GitHub releases: <https://github.com/micro-manager/mm-test-adapters/releases>  

   These releases include just the shared libraries for these adapters.

1. Via a PyPI package:

   ```sh
   pip install mm-test-adapters
   ```

   This package includes the shared libraries, and a single public method,
   `mm_test_adapters.device_adapter_path`, which returns a path to the device
   adapters folder.

## Using PyPI Package

```python
import pymmcore  # or pymmcore_plus
from mm_test_adapters import device_adapter_path

core = pymmcore.CMMCore()
core.setDeviceAdapterSearchPaths([device_adapter_path()])
```

## Build Adapters

To build these locally, you should first have system boost installed:

```sh
# macos
brew install boost
# ubuntu
sudo apt-get install libboost-all-dev
# windows
choco install boost-msvc-14.2
```

```sh
uv sync --no-editable
# or
uv run fetch.py --build
```

## Build Python Package

To build an sdist and wheel, run:

```sh
uv build
```

You may optionally set the env var `MM_SHA` to build a specific commit
of mmCoreAndDevices.

### Cleanup

If you want to remove all external sources and build files:

```sh
make clean
```

> note, the makefile also works on Windows if you have git for windows.

## Using Releases on CI

To use these on CI see <https://github.com/pymmcore-plus/setup-mm-test-adapters>

```yaml
- name: Install MM test adapters
  uses: pymmcore-plus/setup-mm-test-adapters@main
  with:
    # all inputs are optional
    # version should look like:
    #   literal string 'latest'
    #   DIV -> version: 74
    #   DIV.YYYYMMDD -> version: 74.202508
    version: latest
    destination: ./mm-test-adapters
```

## Using Releases Locally

[Download the
release](https://github.com/pymmcore-plus/mm-test-adapters/releases/) you would
like to use, then place it wherever Micro-Manager is looking for device
adapters.

To have them found by pymmcore-plus, place them in the default
[pymmcore-plus](https://github.com/pymmcore-plus/pymmcore-plus) install
location, named `Micro-Manager-YYYYMMDD`

- **Windows**: `$LOCALAPPDATA/pymmcore-plus/pymmcore-plus/mm/Micro-Manager-YYYYMMDD`
- **macOS**: `$HOME/Library/Application Support/pymmcore-plus/mm/Micro-Manager-YYYYMMDD`
- **Linux**: `$HOME/.local/share/pymmcore-plus/mm/Micro-Manager-YYYYMMDD`

> [!TIP]
> On macOS, you will need to give permissions to allow the shared libraries to run:
>
> ```sh
> xattr -r -d com.apple.quarantine ~/Library/Application\ Support/pymmcore-plus/mm/Micro-Manager-*
> ```
>
