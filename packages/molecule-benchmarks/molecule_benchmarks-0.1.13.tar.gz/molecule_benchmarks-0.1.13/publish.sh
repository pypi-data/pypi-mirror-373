#!/bin/bash

set -a
source .env
set +a
rm -rf dist
uv build
uv publish