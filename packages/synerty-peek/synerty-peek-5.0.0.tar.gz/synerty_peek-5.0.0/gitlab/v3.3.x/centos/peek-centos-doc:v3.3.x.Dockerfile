FROM peek-centos:v3.3.x
ENV RELEASE_BRANCH="v3.3.x"

WORKDIR /root

# -----------------------------------------------------------------------------
# Install the dependency for building PDFs from Sphinx
RUN yum install -y texlive
RUN yum install -y texlive-*
RUN yum install -y which 
