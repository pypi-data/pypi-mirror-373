# KaaS CLI

## Simple Installation
Our deployments can be found on [Pypi](https://pypi.org/project/kaas-cli/).

### Installation
`pip install --user kaas-cli`
or 
`sudo pip install kaas-cli`

## For Developers

Prerequisites: `python >= 3.11`, `pip >= 20.0.2`, `poetry >= 1.3.2`.

### Installation

To install the package using `pip`, start by building from [Source](https://github.com/runtimeverification/kaas)

```bash
make build
pip install dist/*.whl
```

### Environment Variables

Configure the CLI by copying the example environment file and setting up the necessary environment variables:

```bash
cp .flaskenv.example .flaskenv
```

Then, edit the `.flaskenv` file to match your settings.


### Usage

After installing the dependencies with `poetry install`, you can spawn a shell using `poetry shell`, or alternatively, use `make`:

```bash
make shell
kaas-cli hello
kaas-cli --version
```

To verify the installation, run `kaas-cli hello`. If you see the message `Hello World!`, the CLI is set up correctly.

### Documentation

For detailed usage instructions of the `kaas-cli` tool, please refer to the official [documentation](https://docs.runtimeverification.com/kaas/guides/kaas-cli_connecting-using-tokens).
