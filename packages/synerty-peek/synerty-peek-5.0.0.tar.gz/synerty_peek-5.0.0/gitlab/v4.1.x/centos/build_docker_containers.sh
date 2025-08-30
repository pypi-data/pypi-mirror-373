#!/usr/bin/env bash

set -o errexit
set -o nounset

IMAGE_NAMES=""
IMAGE_NAMES="${IMAGE_NAMES} peek-centos-sbom:v4.1.x "
IMAGE_NAMES="${IMAGE_NAMES} peek-centos:v4.1.x "
IMAGE_NAMES="${IMAGE_NAMES} peek-centos-test:v4.1.x "
IMAGE_NAMES="${IMAGE_NAMES} peek-centos-sonar:v4.1.x "
IMAGE_NAMES="${IMAGE_NAMES} peek-centos-build:v4.1.x "
IMAGE_NAMES="${IMAGE_NAMES} peek-centos-doc:v4.1.x "

for IMAGE_NAME in ${IMAGE_NAMES}
do
    echo "Building |${IMAGE_NAME}|"

    docker build -t ${IMAGE_NAME} -f ${IMAGE_NAME}.Dockerfile .
    docker tag ${IMAGE_NAME} nexus.synerty.com:5001/${IMAGE_NAME}
    docker push nexus.synerty.com:5001/${IMAGE_NAME}

done
