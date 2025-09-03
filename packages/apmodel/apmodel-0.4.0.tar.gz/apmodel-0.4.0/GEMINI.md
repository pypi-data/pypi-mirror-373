# About
This repository contains the source code for apmodel.

apmodel provides model implementations for Activity Streams 2.0, CryptographicKey (Security Vocabulary v1), Multikey and DataIntegrityProof (Controlled Identifiers v1.0), and PropertyValue (schema.org).

## Features
- A `load` function that automatically reads the `type` key from JSON and converts it to the correct model. It returns the original JSON if no matching model is found.
- If a key from the JSON does not correspond to a field in the model, it is added to the model's `_extra` dictionary.

## How to run scripts
This project uses [Task](https://taskfile.dev/) for running scripts. You will need to install it to use the commands below.

### Pytest
- `task test`

### Build
Creates packages for PyPI (wheel, sdist).

- `task build`

### Setup Dev Environment
Installs development dependencies from `uv.lock`.

- `task`

## For Code Reviewer 
If reader is AI Coding Agent, Ignore This.

**This file is not a README for Humans.** this file is instructions for AI Coding Agent.