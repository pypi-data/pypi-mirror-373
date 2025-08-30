try:
    import kumoai.kumolib  # noqa: F401
except Exception as e:
    import platform

    _msg = f"""RFM is not supported in your environment.

💻 Your Environment:
Python version: {platform.python_version()}
Operating system: {platform.system()}
CPU architecture: {platform.machine()}
glibc version: {platform.libc_ver()[1]}

✅ Supported Environments:
* Python versions: 3.9, 3.10, 3.11, 3.12, 3.13
* Operating systems and CPU architectures:
  * Linux (x86_64)
  * macOS (arm64)
  * Windows (x86_64)
* glibc versions: >=2.28

❌ Unsupported Environments:
* Python versions: 3.8, 3.14
* Operating systems and CPU architectures:
  * Linux (arm64)
  * macOS (x86_64)
  * Windows (arm64)
* glibc versions: <2.28

Please create a feature request at 'https://github.com/kumo-ai/kumo-rfm'."""

    raise RuntimeError(_msg) from e

from typing import Optional, Dict
import os
import kumoai
from .local_table import LocalTable
from .local_graph import LocalGraph
from .rfm import KumoRFM
from .authenticate import authenticate


def init(
    url: Optional[str] = None,
    api_key: Optional[str] = None,
    snowflake_credentials: Optional[Dict[str, str]] = None,
    snowflake_application: Optional[str] = None,
    log_level: str = "INFO",
) -> None:
    if url is None:
        url = os.getenv("KUMO_API_URL", "https://kumorfm.ai/api")

    kumoai.init(url=url, api_key=api_key,
                snowflake_credentials=snowflake_credentials,
                snowflake_application=snowflake_application,
                log_level=log_level)


__all__ = [
    'LocalTable',
    'LocalGraph',
    'KumoRFM',
    'authenticate',
    'init',
]
