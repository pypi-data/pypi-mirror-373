#!/bin/bash

set -eu

cd "$HOME"
# shellcheck disable=SC1091
source "$HOME"/.bashrc
source /opt/conda/etc/profile.d/conda.sh

echo "Cloning from branch: Dev"
git clone -b dev https://gitlab.in2p3.fr/fbi-data/omero-quay.git
cd omero-quay/
conda env create -y -f environment.yml
echo "done creating environment"
# shellcheck disable=SC2102
conda activate quay
pip install -e .[dev]
conda deactivate

cd "$HOME"
# wget https://downloads.openmicroscopy.org/bio-formats/8.1.1/artifacts/bftools.zip
# unzip bftools.zip
# mv bftools/* /opt/conda/envs/quay/bin/
# rmdir bftools
# rm bftools.zip
