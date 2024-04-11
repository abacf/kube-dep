#!/usr/bin/bash -eux

set -o pipefail

# Generate SSH key
ssh-keygen -t ed25519 -C "Staging cluster" -f ./id_staging
ssh-keygen -t ed25519 -C "Production cluster" -f ./id_production

# echo "id_*" >> ../.gitignore

