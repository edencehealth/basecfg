# basecfg

`basecfg` is a Python library designed to simplify and standardize the process of configuring a Python application, particularly a Dockerized application.

Users of this library create a class which inherits from `basecfg.BaseCfg`. For each configuration option an app should support, a type-annotated class attribute is defined using a call to `opt`.

Once a config class is instantiated it automatically populates the configuration from these sources:

1. default values declared in the configuration class
2. a JSON config file (such as a [Kubernetes ConfigMap](https://kubernetes.io/docs/concepts/configuration/configmap/))
3. a `.env` file (in `docker run` envfile format)
4. environment variables
5. docker secrets
6. command-line arguments

## Example

This file is an excerpt from [a more extensive example](docs/example.md) implementation of the library:

```python
#!/usr/bin/env python3
from typing import Optional

from basecfg import BaseCfg, opt


class ExampleAppConf(BaseCfg):
    server_username: str = opt(
        default="demoperson",
        doc="The username to use on the server",
    )
    server_password: Optional[str] = opt(
        default=None,
        doc="The password to use on the server",
        redact=True,
    )
    verbose: bool = opt(
        default=False,
        doc="whether to log verbosely",
    )
    batch_size: Optional[int] = opt(
        default=None,
        doc="how many objects to transfer at a time",
    )
```
