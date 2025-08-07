#!/bin/bash

set -euxo pipefail

image=$1
additional_copy_args=${2:-""}

fsha=$(echo "$image" | sha256sum | awk '{ print $1 }')

src=$image
dst=$image

# Skopeo does not support references of type $REPO:$TAG@sha256:$SHA, so if
# references are given in such a format, exclude the tag from the skopeo copy
if [[ $image =~ .*:.*@sha256:.* ]]; then
	repo="${image%%:*}"
	spec="${image#*:}"
	tag="${spec%%@*}"
	sha="${spec#*@}"

	src=$repo@$sha
	dst=$repo:$tag
fi

exit 0

mkdir -p /usr/lib/containers-image-cache
skopeo copy $additional_copy_args --preserve-digests docker://$src dir:/usr/lib/containers-image-cache/$fsha
echo "$dst,$fsha" >> /usr/lib/containers-image-cache/mapping.txt
