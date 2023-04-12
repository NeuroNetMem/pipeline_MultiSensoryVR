# pipeline_Neuropixel
Preprocessing pipeline for Neuropixel recordings

### Install pykilosort
Install Anaconda and navigate to the directory you want the code to be put
```
git clone -b ibl_prod https://github.com/int-brain-lab/pykilosort.git
git clone https://github.com/guidomeijer/ibl-neuropixel
cd pykilosort
conda env create -f ./pyks2.yml
conda activate pyks2
pip install -e .
pip install cython
pip install ibllib
pip uninstall ibl-neuropixel
cd ..
cd ibl-neuropixel
python setup.py install
```
