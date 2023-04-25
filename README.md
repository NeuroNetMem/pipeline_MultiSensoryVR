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

### Set up your GPU 
Install the NVIDA GPU driver on Windows (https://www.nvidia.com/download/index.aspx). This should (on Windows) be all you need to do.

#### Optional: if the spikesorting does not use the GPU you might need to install CUDA in WSL
If you need to enable CUDA in WSL, on Windows this is a bit tricky. Normally when installing CUDA it comes with a graphics driver. In this case WSL is using the Windows driver so we don't want to do a regular CUDA install inside WSL. Instead we want to install CUDA without the GPU driver.

Open the Microsoft Store and install Ubuntu
Open Ubuntu, it will install itself in WSL on launch
Check if it worked in the PowerShell terminal `wsl -l -v` should now list Ubuntu.

Open Docker and go to Settings > Resources > WSL Integration and check Ubuntu.

Now we need to go into the Linux subsystem and install CUDA there (more info here: https://ubuntu.com/tutorials/enabling-gpu-acceleration-on-ubuntu-on-wsl2-with-the-nvidia-cuda-platform#1-overview). Open a PowerShell terminal and type ``, when you're in Ubuntu do:
```
sudo apt-key del 7fa2af80
wget https://developer.download.nvidia.com/compute/cuda/repos/wsl-ubuntu/x86_64/cuda-wsl-ubuntu.pin
sudo mv cuda-wsl-ubuntu.pin /etc/apt/preferences.d/cuda-repository-pin-600
sudo apt-key adv --fetch-keys https://developer.download.nvidia.com/compute/cuda/repos/wsl-ubuntu/x86_64/3bf863cc.pub
sudo add-apt-repository 'deb https://developer.download.nvidia.com/compute/cuda/repos/wsl-ubuntu/x86_64/ /'
sudo apt-get update
sudo apt-get -y install cuda
```




