FROM peek-centos:v4.1.x
ENV RELEASE_BRANCH="v4.1.x"

WORKDIR /root

# -----------------------------------------------------------------------------
# Install the dependency for building PDFs from Sphinx
RUN dnf install -y texlive
RUN dnf install -y texlive-*
RUN dnf install -y which

# Cleanup the downloaded packages:
RUN dnf clean all