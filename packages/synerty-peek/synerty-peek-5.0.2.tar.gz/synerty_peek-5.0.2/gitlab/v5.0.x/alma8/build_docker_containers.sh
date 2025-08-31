#!/usr/bin/env bash

set -o errexit
set -o nounset

IMAGE_NAMES=""
IMAGE_NAMES="${IMAGE_NAMES} peek-alma8:v5.0.x "
IMAGE_NAMES="${IMAGE_NAMES} peek-alma8-test:v5.0.x "
IMAGE_NAMES="${IMAGE_NAMES} peek-alma8-build:v5.0.x "
IMAGE_NAMES="${IMAGE_NAMES} peek-alma8-doc:v5.0.x "

for IMAGE_NAME in ${IMAGE_NAMES}
do
    echo "Building |${IMAGE_NAME}|"

    docker build -t ${IMAGE_NAME} -f ${IMAGE_NAME}.Dockerfile .
    docker tag ${IMAGE_NAME} nexus.synerty.com:5001/${IMAGE_NAME}
    docker push nexus.synerty.com:5001/${IMAGE_NAME}

done
