#!/usr/bin/env bash

set -ef -o pipefail

source "$HOME"/.bashrc
source /opt/conda/etc/profile.d/conda.sh
conda activate quay

exec "$@"
