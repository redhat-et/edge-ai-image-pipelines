#!/bin/bash

set -euxo pipefail

image=$1
repo="${image%%:*}"
spec="${image#*:}"
tag="${spec%%@*}"
sha="${spec#*@}"

additional_copy_args=${2:-""}

mkdir -p /usr/lib/containers-image-cache
skopeo copy $additional_copy_args --preserve-digests docker://$repo@$sha dir:/usr/lib/containers-image-cache/$sha
echo "$repo:$tag,$sha" >> /usr/lib/containers-image-cache/mapping.txt
