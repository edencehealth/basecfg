# basecfg example

The following files show an example implementation of the library. The example is meant to hilight the various ways the app can accept configuration:

1. default values declared in the configuration class
2. a JSON config file (such as a [Kubernetes ConfigMap](https://kubernetes.io/docs/concepts/configuration/configmap/))
3. a `.env` file (in `docker run` format)
4. environment variables
5. docker secrets
6. command-line arguments


## src/main.py

```python
#!/usr/bin/env python3
from appconf import ExampleAppConf


def main():
    conf = ExampleAppConf(
        json_config_path="/tmp/configmap.json",
        prog="exampleapp",
        version="1.2.3",
    )
    print(f'Username: "{conf.server_username}";  password:"{conf.server_password}";')
    print(f"Verbose?: {conf.verbose!r}; Batch Size: {conf.batch_size!r}")


if __name__ == "__main__":
    main()
```

## src/appconf.py

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

## Dockerfile

```Dockerfile
FROM python:3-alpine

COPY src /app/
ENV PYTHONPATH="/app"
RUN set -eux; \
  python3 -m venv /app/venv; \
  . /app/venv/bin/activate; \
  pip install basecfg;

ENTRYPOINT [ "/app/venv/bin/python3", "/app/main.py" ]
```

## configmap.json

```json
{
    "batch_size": 42
}
```

## docker-compose.yml

```yaml
services:
  app:
    build: .
    secrets:
      - server_password
    environment:
      SERVER_USERNAME: "demouser3"
    volumes:
      - "./configmap.json:/tmp/configmap.json:ro"

secrets:
  server_password:
    file: ./.secret-server_password
```

## Automatic Usage Text

The following text is generated when invoking the container with the `--help` argument.

```
usage: exampleapp [-h] [--version] [--server-username SERVER_USERNAME]
                  [--server-password SERVER_PASSWORD]
                  [--verbose | --no-verbose] [--batch-size BATCH_SIZE]

options:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  --server-username SERVER_USERNAME
                        The username to use on the server (default demoperson)
  --server-password SERVER_PASSWORD
                        The password to use on the server (default None)
  --verbose, --no-verbose
                        whether to log verbosely (default False)
  --batch-size BATCH_SIZE
                        how many objects to transfer at a time (default None)
```

## Invocation

This example invocation shows using command-line arguments.

```shell=/bin/sh
$ docker compose run --build app --verbose
Username: "demouser3";  password:"hummus monsieur tiptoeing";
Verbose?: True; Batch Size: 42
$
```
