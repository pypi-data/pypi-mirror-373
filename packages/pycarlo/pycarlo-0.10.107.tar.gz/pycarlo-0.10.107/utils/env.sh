#!/usr/bin/env sh
set -e

BASEDIR=$(dirname "$0")

. "$BASEDIR/.env"

if [ -z "${MCD_API_ENDPOINT}" ]; then echo 'Missing expected .env variable of "MCD_API_ENDPOINT".' && exit 1; fi
if [ -z "${MCD_DEFAULT_API_ID}" ]; then echo 'Missing expected .env variable of "MCD_DEFAULT_API_ID".' && exit 1; fi
if [ -z "${MCD_DEFAULT_API_TOKEN}" ]; then echo 'Missing expected .env variable of "MCD_DEFAULT_API_TOKEN".' && exit 1; fi

MCD_API_ENDPOINT="${MCD_API_ENDPOINT}" MCD_DEFAULT_API_ID="${MCD_DEFAULT_API_ID}" MCD_DEFAULT_API_TOKEN="${MCD_DEFAULT_API_TOKEN}" exec "$@"
