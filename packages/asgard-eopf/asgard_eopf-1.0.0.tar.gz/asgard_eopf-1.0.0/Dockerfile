# Copyright 2023 ESA
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# This Dockerfile is used to build the Dask runtime environment
# allowing to run ASGARD on the EOPF cluster.
# The build relies on the ASGARD wheel which must be available
# in the current directory.

# The Dockerfile relies on Docker's multi-stage build feature:
# https://docs.docker.com/build/building/multi-stage/
#
# Currently, there is a known problem with pre-stages not being cached.
# See this link for more information: https://snyk.io/blog/best-practices-containerizing-python-docker/
# and the section "Known issues with multi-stage builds for containerized Python applications".
#
# Thus, please run the following commands to build the image:
#
#   export DOCKER_BUILDKIT=1
#   export BUILDKIT_PROGRESS=plain
#   docker build -t asgard:multi-stage --cache-from asgard:multi-stage --build-arg BUILDKIT_INLINE_CACHE=1 .

# Build stage
FROM registry.eopf.copernicus.eu/sde/python-build-environment:latest as build
# FROM registry.eopf.copernicus.eu/sde/dask-container-images/dask-scheduler-worker:latest as build

# Due to presence of tests folder in eopf, tests from ASGARD are not recognize if eopf test folder is not rm:
# https://gitlab.eopf.copernicus.eu/sde/python-build-environment/-/issues/4
RUN rm -Rf /home/eopf/.local/lib/python3.11/site-packages/tests/

USER root

ARG PIP_EXTRA_INDEX_URL

# Install the ASGARD from its wheel.
# This package must be available in the current directory.
#
# This solution has been chosen to allow building an image for the latest state
# of the current branch without previously uploading a fixed version of the
# corresponding Python package into the package registry,
# thus simplifying the testing of a branch.
COPY dist/asgard_eopf-*.whl /tmp/

# Skip the "bin not on PATH" warning: This is only a build container.
RUN pip install --user --no-cache-dir --no-warn-script-location /tmp/asgard_eopf-*.whl

# Final stage
#
# Use the EOPF Dask image to assure that the Dask dependencies
# are aligned with the Dask version actually deployed.
FROM registry.eopf.copernicus.eu/sde/dask-container-images/dask-scheduler-worker:latest

# OCI annotations
# See https://github.com/opencontainers/image-spec/blob/main/annotations.md#pre-defined-annotation-keys
ARG CI_COMMIT_SHA
LABEL org.opencontainers.image.title="ASGARD Dask runtime"
LABEL org.opencontainers.image.description="Dask runtime environment including the ASGARD library"
LABEL org.opencontainers.image.source="https://gitlab.eopf.copernicus.eu/geolib/asgard/"
LABEL org.opencontainers.image.url="https://gitlab.eopf.copernicus.eu/geolib/asgard/-/blob/main/Dockerfile"
LABEL org.opencontainers.image.revision="$CI_COMMIT_SHA"
LABEL org.opencontainers.image.vendor="ESA"
LABEL org.opencontainers.image.authors="CS Group"
LABEL org.opencontainers.image.base.name="registry.eopf.copernicus.eu/sde/dask-container-images/dask-scheduler-worker:latest"

# Copy all installed Python packages into the final image
COPY --from=build --chown=dask:dask /root/.local /home/dask/.local/
