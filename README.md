# ![dotrun](https://assets.ubuntu.com/v1/9dcb3655-dotrun.png?w=100 "dotrun") Docker image


This project is a docker image for developing Node.js and Python web projects. It is an essential tool for the Canonical web team local development.

## Image Features

- Based on ubuntu:focal
- Python 3.10
- Node 20 LTS
- Yarn
- dotrun-docker

### dotrun-docker:

dotrun-docker is a Python package inside the Docker image. It simplifies running Canonical web projects:

- Make use of standard `package.json` script entrypoints:
  - `dotrun` runs `yarn run start`
  - `dotrun foo` runs `yarn run foo`
- Detect changes in `package.json` and only run `yarn install` when needed
- Detect changes in `requirements.txt` and only run `pip3 install` when needed
- Run scripts using environment variables from `.env` and `.env.local` files
- Keep python dependencies in `.venv` in the project folder for easy access

## Usage

Before running this image locally, you should know that it is an essential part of [dotrun](https://github.com/canonical/dotrun), our python package for running Canonical websites. If you are interested in running our web projects, visit our [dotrun](https://github.com/canonical/dotrun) repository.

If you prefer to access this image directly and work on it, then you can run it and access a bash environment with:
```bash
docker run -it canonicalwebteam/dotrun-image:latest /bin/bash
```

These are the `dotrun-docker` commands available inside our image:

```bash
$ dotrun          # Install dependencies and run the `start` script from package.json
$ dotrun clean    # Delete `node_modules`, `.venv`, `.dotrun.json`, and run `yarn run clean`
$ dotrun install  # Force install node and python dependencies
$ dotrun exec     # Start a shell inside the dotrun environment
$ dotrun exec {command}          # Run {command} inside the dotrun environment
$ dotrun {script-name}           # Install dependencies and run `yarn run {script-name}`
$ dotrun -s {script}             # Run {script} but skip installing dependencies
$ dotrun --env FOO=bar {script}  # Run {script} with FOO environment variable
```

## Building/Testing

To QA any changes to this image, you probably want to build a local image with Docker:

`docker build . --tag canonicalwebteam/dotrun-image:local`

### Using python

You should probably create a virtualenv, and then install dotrun-docker.
```bash
pip uninstall dotrun-docker
cd src
pip install .
```

## Using this image with dotrun

`dotrun-image` can be used with `dotrun 2.3.0`  by building a docker image, and specifying the local image name when running dotrun, for example:
```bash
docker build . --tag canonicalwebteam/dotrun-image:local
cd snapcraft.io
dotrun --image canonicalwebteam/dotrun-image:local install
dotrun --image canonicalwebteam/dotrun-image:local serve
```

## Releasing

Changes to the default branch will trigger a new release using GitHub Actions.

- Released to [Docker Hub canonicalwebteam/dotrun-image](https://hub.docker.com/r/canonicalwebteam/dotrun-image/)
- Architectures: AMD64 and ARM64

### Releasing specific versions

Update the version in setup.py, and push the changes to a new branch called `release/<version>` e.g `release/1.2.0-rc1`. This will trigger a new release and publish the tagged image to dockerhub.

