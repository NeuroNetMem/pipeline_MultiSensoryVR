# pipeline_Neuropixel
Preprocessing pipeline for Neuropixel recordings

### Install SpikeInterface
Install Miniforge (https://github.com/conda-forge/miniforge#mambaforge)

Open the Miniforge terminal and do:
```
mamba create -n spikeinterface python=3.10
mamba activate spikeinterface
pip install spikeinterface[full,widgets]
pip install git
git clone https://github.com/NeuroNetMem/pipeline_Neuropixel
pip install docker
pip install ibllib
pip install spikeinterface-gui
```

### Set up Docker
Instructions to set up Docker (for Windows):

Install Docker Desktop (https://www.docker.com/products/docker-desktop/)

Create an account on Docker Hub (https://hub.docker.com/)

Install WSL2; open a PowerShell terminal and type
```
wsl --install 
```


