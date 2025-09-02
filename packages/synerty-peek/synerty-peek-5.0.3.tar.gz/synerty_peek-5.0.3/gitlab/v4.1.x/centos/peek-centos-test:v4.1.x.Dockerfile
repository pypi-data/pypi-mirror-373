FROM peek-centos:v4.1.x
ENV RELEASE_BRANCH="v4.1.x"

WORKDIR /root

# Download and install the pinned packages for this release
#
RUN wget "https://gitlab.synerty.com/peek/peek/-/raw/${RELEASE_BRANCH}/gitlab/${RELEASE_BRANCH}/requirements/release_pinned_peek_requirements.txt"
RUN pip install -r release_pinned_peek_requirements.txt

# Install global python requirements
RUN pip install Cython virtualenv wheel pip-tools pipx build

# Install the unit test report converters
RUN pip install subunitreporter junitxml ddt
