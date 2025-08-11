#!/bin/bash

set -euxo pipefail

image=$1
additional_copy_args=${@:2}

fsha=$(echo "$image" | sha256sum | awk '{ print $1 }')

src=$image
dst=$image

# Skopeo does not support references of type $REPO:$TAG@sha256:$SHA, so if
# references are given in such a format, exclude the tag from the skopeo copy
# 
# Unfortunately, this means that if there are two images $REPO:$TAG@sha256:$FIRST_SHA and $REPO:$TAG@sha256:$SECOND_SHA
# Only the second image will be available.
#
# Hopefully anybody advanced enough to run into this issue is also advanced enough to find there way to this file and read
# this comment
if [[ $image =~ .*:.*@sha256:.* ]]; then
	repo="${image%%:*}"
	spec="${image#*:}"
	tag="${spec%%@*}"
	sha="${spec#*@}"

	src=$repo@$sha
	dst=$repo:$tag
fi

mkdir -p /usr/lib/containers-image-cache
skopeo copy --multi-arch=all --preserve-digests $additional_copy_args docker://$src dir:/usr/lib/containers-image-cache/$fsha
echo "$dst,$fsha" >> /usr/lib/containers-image-cache/mapping.txt
