# planqk-commons

Set of common utilities and classes to boost development of quantum computing applications using PLANQK.

## Development

### Setup

```bash
uv venv
source .venv/bin/activate

uv lock
uv sync
```

Update dependencies and lock files:

```bash
uv sync -U
```

### Run tests

```bash
pytest
```

### Export dependencies to requirements files

> This is useful to keep the project independent of the `uv` tool.
> Developers can install the dependencies using `pip install -r requirements.txt` and `pip install -r requirements-dev.txt`.
> Further, they may use a different tool to manage virtual environments.

```bash
uv export --format requirements-txt --no-dev --no-emit-project > requirements.txt
uv export --format requirements-txt --only-dev --no-emit-project > requirements-dev.txt
```

### Docker

Build the image:

```bash
docker build -t planqk-commons .
```

Run interactive shell:

```bash
docker run -it -v "$(pwd)/user_code:/workspace" planqk-commons
```

Generate OpenAPI description:

```bash
docker run -v "$(pwd)/user_code:/workspace" planqk-commons openapi
```

You can also use the pre-built image:

```bash
docker run -it -v "$(pwd)/user_code:/workspace" registry.gitlab.com/planqk-foss/planqk-commons:latest
```

## License

Apache-2.0 | Copyright 2024-present Kipu Quantum GmbH
