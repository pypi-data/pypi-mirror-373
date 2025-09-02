# Use Python 3.12 as base image
FROM python:3.12-slim

# Build argument for version (defaults to latest)
ARG VERSION=latest

# Set working directory inside container
WORKDIR /app

# Install the co-datascientist package from PyPI
# If VERSION is "latest", install the latest version
# Otherwise, install the specific version
RUN if [ "$VERSION" = "latest" ]; then \
        pip install --no-cache-dir co-datascientist; \
    else \
        pip install --no-cache-dir co-datascientist==$VERSION; \
    fi

# Create a directory for user scripts
RUN mkdir -p /workspace

# Set the working directory to where users will mount their files
WORKDIR /workspace

# Add labels for better metadata
LABEL org.opencontainers.image.title="Co-DataScientist"
LABEL org.opencontainers.image.description="AI-powered tool for agentic recursive model improvement"
LABEL org.opencontainers.image.url="https://github.com/TropiFloAI/co-datascientist"
LABEL org.opencontainers.image.source="https://github.com/TropiFloAI/co-datascientist"
LABEL org.opencontainers.image.version="$VERSION"

# Set default command to show help
CMD ["co-datascientist", "--help"] 