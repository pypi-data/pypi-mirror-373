FROM python:3.8-slim-bookworm
# Install prerequisites
RUN apt-get update -y && \
    apt-get install -y \
    patch \
    gcc && \
    apt-get install -y --no-install-recommends \
    g++ \
    git && \
# Final upgrade + clean
    apt-get update -y && \
    apt-get clean all -y

# Enable Installing packages as root
ENV FLIT_ROOT_INSTALL=1

# Add pyproject.toml + README.md for flit install
ADD pyproject.toml pyproject.toml
ADD README.md README.md
