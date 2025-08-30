#!/usr/bin/env bash

PY_PACKAGE="peek_admin_app"
PYPI_PUBLISH="1"

VER_FILES_TO_COMMIT=""

VER_FILES=""
VER_FILES="${VER_FILES} peek_admin_app/package.json"
VER_FILES="${VER_FILES} peek_admin_app/src/environments/peek-app-environment.ts"
