# Dockerfile
FROM mcr.microsoft.com/dotnet/sdk:6.0

ARG SBOM_TOOL_VERSION=2.2.7

RUN apt-get update
RUN apt-get install -y wget unzip

ENV URL="https://github.com/microsoft/sbom-tool/releases/download"
RUN wget ${URL}/v${SBOM_TOOL_VERSION}/sbom-tool-linux-x64


RUN chmod +x sbom-tool-linux-x64
RUN mv sbom-tool-linux-x64 /usr/local/bin/sbom-tool
RUN apt-get clean
RUN rm -rf /var/lib/apt/lists/*




# Create a run.sh script with a heredoc
# Create a run.sh script
RUN echo '#!/bin/bash' > /run.sh
RUN echo 'set -x' >> /run.sh
RUN echo 'rm -rf /src/_manifest' >> /run.sh
# TODO: Docker contianer arguments will be $1, $2, etc here
# TODO: Use it for the version
RUN echo 'sbom-tool \\' >> /run.sh
RUN echo '         generate \\' >> /run.sh
RUN echo '         -b /src \\' >> /run.sh
RUN echo '         -bc /src \\' >> /run.sh
RUN echo '         -nsb https://peek.synerty.com \\' >> /run.sh
RUN echo '         -ps "Synerty HQ Pty Ltd" \\' >> /run.sh
RUN echo '         -pn "synerty-peek" \\' >> /run.sh
RUN echo '         -pv "4.0.0-rc" \\' >> /run.sh
RUN echo '         -pm true \\' >> /run.sh
RUN echo '         -li true \\' >> /run.sh
RUN echo '         -V Verbose' >> /run.sh
RUN echo 'pushd /src/_manifest/spdx_2.2' >> /run.sh

RUN echo 'popd' >> /run.sh

# Make the run.sh script executable
RUN chmod +x /run.sh

# Add a new entry point to run the script
ENTRYPOINT ["/run.sh"]

