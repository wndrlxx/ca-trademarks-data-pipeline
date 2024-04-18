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

if [ -z "$GCP_REGION" ]; then
    echo "Error: GCP_REGION environment variable is not set."
    exit 1
fi

sed -i '' "s/project: [^[:space:]]*/project: $PROJECT_ID/g" "$PROFILES_YML_PATH"
sed -i '' "s/location: [^[:space:]]*/location: $GCP_REGION/g" "$PROFILES_YML_PATH"