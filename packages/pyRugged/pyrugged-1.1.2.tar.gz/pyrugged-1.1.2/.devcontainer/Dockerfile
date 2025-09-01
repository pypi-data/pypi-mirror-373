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

# Use AWS repo to fix ASGARD VM's Docker "Too many requests" issue
# https://stackoverflow.com/a/65806626
# https://gallery.ecr.aws/debian/debian
FROM public.ecr.aws/debian/debian:12
ENV LC_ALL=C

# install run dep
RUN apt-get update && apt-get upgrade -y && apt-get install --no-install-recommends -y python3.11
# install build dep
RUN apt-get install --no-install-recommends -y python3.11-dev gcc unzip
# install dev dep
RUN apt-get install --no-install-recommends -y python3.11-venv git less vim bash-completion

# setup non root user
RUN useradd -ms /bin/bash vscode

# alt: mcr.microsoft.com/devcontainers/base:dev-debian-12
# https://mcr.microsoft.com/en-us/artifact/mar/devcontainers/base/tags
