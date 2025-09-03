# taggie 🖍️

<!-- BADGIE TIME -->

[![pipeline status](https://img.shields.io/gitlab/pipeline-status/saferatday0/sandbox/taggie?branch=main)](https://gitlab.com/saferatday0/sandbox/taggie/-/commits/main)
[![coverage report](https://img.shields.io/gitlab/pipeline-coverage/saferatday0/sandbox/taggie?branch=main)](https://gitlab.com/saferatday0/sandbox/taggie/-/commits/main)
[![latest release](https://img.shields.io/gitlab/v/release/saferatday0/sandbox/taggie)](https://gitlab.com/saferatday0/sandbox/taggie/-/releases)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)
[![cici enabled](https://img.shields.io/badge/%E2%9A%A1_cici-enabled-c0ff33)](https://gitlab.com/saferatday0/cici)
[![code style: prettier](https://img.shields.io/badge/code_style-prettier-ff69b4.svg)](https://github.com/prettier/prettier)

<!-- END BADGIE TIME -->

It's like Badgie, but for **tags!**

## About

taggie tags things. It's what it does.

taggie is built as a standalone tool to be integrated into a larger toolchain
for analyzing and acting on project contents.

## Installation

```sh
python3 -m pip install taggie
```

## Usage

### Use the default tags

Run `taggie` with no options to use the default collection of tag files bundled
with the application:

```sh
taggie
```

```console
$ taggie
TOTAL    NAME              EXAMPLE
243      yaml              marp/.gitlab-ci.yml
52       markdown          container/README.md
15       opentofu          opentofu/outputs.tf
11       jinja             container/.cici/README.md.j2
9        python            python/examples/dynamic-version/python_pipeline/__init__.py
6        toml              python/examples/dynamic-version/pyproject.toml
3        html              zola/templates/index.html
1        restructuredtext  sphinx/docs/index.rst
1        css               marp/style.css
```

### Use your own tags

Define a set of tagging rules in YAML files we like to call "tag files":

```yaml
# jinja.yaml
- type: file.extension
  tags:
    - jinja
  extensions:
    - j2
```

The syntax is a little verbose, but that's because we want to make the tagging
components pluggable.

Run `taggie` with the `-t`/`--tag-file` option to specify your tag files. A
directory can also be passed. `-t`/`--tag-file` can be specified as many times
as needed:

```sh
taggie -t jinja.yaml
```

```console
$ taggie -t jinja.yaml
TOTAL    NAME    EXAMPLE
11       jinja   gitlab/.cici/README.md.j2
```

## License

Copyright 2025 UL Research Institutes.

Licensed under the Apache License, Version 2.0 (the "License"); you may not use
this file except in compliance with the License. You may obtain a copy of the
License at

<http://www.apache.org/licenses/LICENSE-2.0>

Unless required by applicable law or agreed to in writing, software distributed
under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
