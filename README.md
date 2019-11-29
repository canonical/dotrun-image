# canonicalwebteam/dev docker image

A docker image as a basis for Canonical webteam's local development tools.

## Features

- Based on ubuntu:bionic
- Python3
- NodeJS version 12.X LTS
- Yarn
- Ruby

## Testing

Before releasing this image to the repository you'll want to test it locally.

From within the root folder of the project run the following, where `<next tag>` is the next available tag. You can find out what that should by by visiting https://hub.docker.com/r/canonicalwebteam/dev/tags.

`docker build . --tag canonicalwebteam/dev:<next tag>`

Navigate to a local project you'd like to test with and update the following line in the `run` script with the new tag name.

`dev_image="canonicalwebteam/dev:<next tag>"`

Then run that project and ensure it works as expected.

`./run`

## Releasing

Once you have verified that the container works for a few different projects you can push it up to the Docker Hub

`docker login`

`docker push canonicalwebteam/dev:<next tag>`

After the push has completed successfully after a few minutes verify that the image is on the hub https://hub.docker.com/r/canonicalwebteam/dev/tags?page=1&name=<next tag>. Then remove your local copy of the image and try running one of the projects from before. It should download the image and run as before.
