#!/bin/bash

set -eu

cd "$HOME"
wget https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh
chmod +x Miniforge3-Linux-x86_64.sh
./Miniforge3-Linux-x86_64.sh -b
# shellcheck disable=SC1091
source miniforge3/bin/activate
conda init
# shellcheck disable=SC1091
source "$HOME"/.bashrc
echo "Cloning from branch: Dev"
git clone -b dev https://gitlab.in2p3.fr/fbi-data/omero-quay.git
cd omero-quay/
conda env create -y -f environment.yml
echo "done creating environment"
conda activate quay

# shellcheck disable=SC2102
pip install -e .[server]
conda deactivate
cd "$HOME"
wget https://downloads.openmicroscopy.org/bio-formats/7.3.0/artifacts/bftools.zip
unzip bftools.zip
mv bftools/* miniforge3/envs/quay/bin/
rmdir bftools
rm bftools.zip
