#!/bin/bash

set -euxo pipefail

while IFS="," read -r image sha
do
	skopeo copy --preserve-digests dir:/usr/lib/containers-image-cache/$sha containers-storage:$image
done < /usr/lib/containers-image-cache/mapping.txt
