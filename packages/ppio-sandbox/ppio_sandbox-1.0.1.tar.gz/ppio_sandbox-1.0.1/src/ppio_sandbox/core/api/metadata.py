import platform

from importlib import metadata

package_version = metadata.version("ppio_sandbox")

default_headers = {
    "lang": "python",
    "lang_version": platform.python_version(),
    "machine": platform.machine(),
    "os": platform.platform(),
    "package_version": metadata.version("ppio_sandbox"),
    "processor": platform.processor(),
    "publisher": "PPIO",
    "release": platform.release(),
    "sdk_runtime": "python",
    "system": platform.system(),
}
