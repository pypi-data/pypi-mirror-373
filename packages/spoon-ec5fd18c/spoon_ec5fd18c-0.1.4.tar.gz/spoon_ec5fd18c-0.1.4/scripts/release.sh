#!/bin/bash

set -eux -o pipefail

uv build
md5sum dist/*
: uv publish
