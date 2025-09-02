![Header](./docs/header.png)

# opencloudtool

[![Actions status](https://github.com/21inchLingcod/opencloudtool/actions/workflows/postsubmit.yml/badge.svg)](https://github.com/21inchLingcod/opencloudtool/actions)
[![codecov](https://codecov.io/github/opencloudtool/opencloudtool/graph/badge.svg?token=J8XGW0T1LC)](https://codecov.io/github/opencloudtool/opencloudtool)

A tool to hide the complexity of the cloud.

## Install `oct-cli`

```bash
curl -LsSf https://repo.opencloudtool.com/install.sh | sh
```

or

```bash
wget -qO- https://repo.opencloudtool.com/install.sh | sh
```

Optional [install as Python library.](/crates/oct-py/README.md)

## Log in to AWS

Basic login ([docs](https://awscli.amazonaws.com/v2/documentation/api/latest/reference/configure/index.html)):

```bash
aws configure
```

Using AWS SSO ([docs](https://awscli.amazonaws.com/v2/documentation/api/latest/reference/configure/sso.html)):

```bash
aws configure sso
```

## Deployment Examples

- [Multiple REST services on the same host with NGINX load balancer](./examples/projects/single-host-rest-service-with-lb/)
- [Multiple REST services on different hosts with NGINX load balancer](./examples/projects/multi-host-rest-service-with-lb/)
- [S3 remote state storage](./examples/projects/s3-remote-state-storage/)
- [REST service with domain](./examples/projects/rest-service-with-domain/)
- [Single host multi services with domains](./examples/projects/single-host-multi-services-with-domains/)
- [Ray single worker](./examples/projects/ray-single-worker/)
- [Inject system env variables](./examples/projects/inject-system-env-var/)
- [HTTP server with single dockerfile](./examples/projects/http-server-with-dockerfile/)
- [HTTP server with multiple dockerfiles](./examples/projects/http-server-with-multiple-dockerfiles/)

## High Level Design

![OpenCloudTool Design](./docs/high-level-design.excalidraw.png)

## Versions Design

Each version of OpenCloudTool has a mini-project to prove the design and implementation.

### v0.5.0 "Refactor: Deployment speed and scalability"

![v0.5.0](./docs/v0.5.0.excalidraw.png)

## Development

### Command examples

#### Install pre-commit hooks

```bash
pre-commit install
```

#### Build project

```bash
 cargo build
```

#### Run deploy command

```bash
 cd dir/with/oct.toml
 cargo run -p oct-cli deploy
```

#### Run destroy command

```bash
 cargo run -p oct-cli destroy
```

#### Show all available commands

```bash
 cargo run -p oct-cli --help
```

#### Show all available parameters for command

```bash
 cargo run -p oct-cli command --help
```

For example:

```bash
 cargo run -p oct-cli deploy --help
```

### Python Library Development

#### How it works: Python-Rust binding

#### The connection between Python and Rust is managed by `maturin` and `PyO3`

1. `maturin` compiles the Rust code in the `oct-py` crate into a native Python module.
2. We configure the name of this compiled module in `pyproject.toml` to be `oct._internal`.
3. The leading underscore (`_`) is a standard Python convention that signals that `_internal` is a low-level module not meant for direct use.
4. Our user-facing Python code in `oct/py_api.py` imports functions from `_internal` and presents them as a clean, stable API.

#### 1. Navigate to the Python Directory

```bash
cd crates/oct-py
```

#### 2. Create and activate the Virtual environment

```bash
uv venv

source .venv/bin/activate # Windows: .venv\Scripts\activate
```

#### 3. Install dependencies

```bash
uv sync --group dev
```

#### 4. Build the Library

```bash
maturin develop
```

#### 5. Run the example

```bash
cd ../../examples/projects/single-host-python-lib
```

You can now run `python deploy.py` or `python destroy.py` to test your changes.

### Releasing the Python Library

#### Bump the Version Number

1. Before releasing, you must increment the version number. PyPI will not accept a version that already exists. Update the version in both
   of these files to keep them synchronized:

- `crates/oct-py/pyproject.toml`
- `crates/oct-py/Cargo.toml`

2. Build & upload the Release Packages:

```bash
maturin sdist

maturin build --release

twine upload target/sdist/* target/wheels/*
```

### Writing tests

[WIP] Main principles:

- Each module provides its own mocks in a public `mocks` module

```rust
...main code...

pub mod mocks {
    ...mocks...
}

#[cfg(test)]
mod tests {
    ...tests...
}
```

- Each module tests cover only the functionality in the module
- If a module uses external modules, they are mocked using mocks provided by the imported module's `mocks` module

```rust
...other imports...

#[cfg(test)]
use module::mocks::MockModule as Module;
#[cfg(not(test))]
use module::Module;

...main code...
```

### Imports ordering

When importing modules, the following order should be used:

- Standard library imports
- Third-party imports
- Local crate imports

```rust
use std::fs;

use serde::{Deserialize, Serialize};

use crate::aws::types::InstanceType;
```

## Dev tools

### Machete

Removes unused dependencies

```bash
cargo install cargo-machete
cargo machete
```

### Cargo Features Manager

Removes unused features

```bash
cargo install cargo-features-manager
cargo features prune
```

### Profile building time

Produces HTML file with building time report.
Can be found in `target/cargo-timings.html`

```bash
cargo build -p PACKAGE_NAME --release --timings
```

## Pricing comparison

This section compares the cost of running a set of services in a cloud with different
approaches which do not require the end user to manage underlying infrastructure (serverless).

**Note that OpenCloudTool is a free to use open-source tool and there is no charge for using it.**

### Simple REST service

Main components:

- Django REST service (0.5 vCPU, 1GB RAM)
- Celery worker (0.5 vCPU, 1GB RAM)
- Redis (0.5 vCPU, 1GB RAM)
- Postgres (0.5 vCPU, 1GB RAM)
- Load Balancer (nginx, ELB, etc.)

#### AWS ECS Fargate

- 2 vCPU (1 vCPU per hour - $0.04048) - $61.5 per month
- 4 GB RAM (1 GB RAM per hour - $0.004445) - $13.5 per month
- Load Balancer ($0.0225 per hour) - $17 per month

Total: $92 per month

#### Single EC2 instance managed by OpenCloudTool

- 1 EC2 [t4g.medium](https://aws.amazon.com/ec2/pricing/on-demand/) instance ($0.0336 per hour): $25.5 per month

Total: $25.5 per month
