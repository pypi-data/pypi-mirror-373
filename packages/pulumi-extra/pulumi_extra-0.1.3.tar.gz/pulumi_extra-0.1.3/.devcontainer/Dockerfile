FROM mcr.microsoft.com/devcontainers/python:1-3.13-bookworm

# Install Pulumi CLI
RUN curl --location --silent --show-error --fail https://get.pulumi.com | sudo sh -s -- --install-root /usr/local

# Install uv
RUN pipx install uv
