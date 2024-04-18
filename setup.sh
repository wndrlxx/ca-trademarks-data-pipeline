#!/bin/bash

PROFILES_YML_PATH="./dags/dbt/ca_trademarks_dp/profiles.yml"

# Check if the file exists
if [ ! -f "$PROFILES_YML_PATH" ]; then
    echo "Error: File profiles.yml not found in dags/dbt/ca_trademarks_dp/"
    exit 1
fi

if [ -z "$PROJECT_ID" ]; then
    echo "Error: PROJECT_ID environment variable is not set."
    exit 1
fi

sed -i -e "s/project: [^[:space:]]*/project: $PROJECT_ID/g" "$PROFILES_YML_PATH"
