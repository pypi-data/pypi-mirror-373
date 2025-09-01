# Stage 1: Build stage
FROM rockylinux:9.3-minimal AS build

# Install necessary build tools
RUN microdnf install -y curl tar wget

# Download the hatch tar.gz file from GitHub
RUN curl -L https://github.com/pypa/hatch/releases/latest/download/hatch-x86_64-unknown-linux-gnu.tar.gz -o /tmp/hatch-x86_64-unknown-linux-gnu.tar.gz

# install yq
RUN VERSION="v4.45.4"                                                                               && \
    BINARY="yq_linux_amd64"                                                                         && \
    wget --quiet https://github.com/mikefarah/yq/releases/download/${VERSION}/${BINARY}.tar.gz -O - |\
    tar xz && mv ${BINARY} /usr/bin/yq   

# Extract the hatch binary
RUN tar -xzf /tmp/hatch-x86_64-unknown-linux-gnu.tar.gz -C /tmp/

# Stage 2: Final stage
FROM rockylinux:9.3-minimal

# Install runtime dependencies
RUN microdnf install -y --nodocs nodejs && \
    microdnf clean all && \
    curl -L https://github.com/jqlang/jq/releases/download/jq-1.8.1/jq-linux-amd64 -o /usr/bin/jq && \
    chmod +x /usr/bin/jq

# Set up a default user and home directory
ENV HOME=/home/neo

# Create a user with UID 1001, group root, and a home directory
RUN useradd -u 1001 -r -g 0 -m -d ${HOME} -s /sbin/nologin \
        -c "Default neo User" neo && \
    mkdir -p /app && \
    mkdir -p /prod && \
    chown -R 1001:0 /app && \
    chmod g+rwx ${HOME} /app

# Copy the hatch binary from the build stage
COPY --from=build /tmp/hatch /usr/bin/hatch
COPY --from=build /usr/bin/yq /usr/bin/yq

# Ensure the hatch binary is executable
RUN chmod +x /usr/bin/hatch

# Switch to the non-root user
USER neo

# Copy the application files into the /app directory
COPY --chown=1001:0 . /app
WORKDIR /app

# Set up virtual environment paths
ENV VIRTUAL_ENV=/app/envs/eoap-cwlwrap
ENV PATH="$VIRTUAL_ENV/bin:$PATH"



# Prune any existing environments and create a new production environment
RUN hatch env prune && \
    hatch env create prod && \
    hatch run prod:eoap-cwlwrap --help && \
    rm -fr /app/.git /app/.pytest_cache

RUN hatch run prod:eoap-cwlwrap --help

WORKDIR /app

