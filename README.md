
# KLTN

## Installation

Source supports following OS with **GPU/CUDA** enabled.
- Ubuntu.

Source require:
- Anaconda 4.10.3 
- python 3.9
- node 14.4.0

### Install source code

```bash
git clone https://github.com/vinhbestever/KTTN.git
pip install -r MONAILabel/requirements.txt
export PATH=$PATH:`pwd`/MONAILabel/monailabel/scripts
```


```bash
cd plugins/ohif
sudo sh requirements.sh # installs yarn
sh build.sh

sudo apt-get install orthanc orthanc-dicomweb -y
sudo apt-get install plastimatch -y
```

### Run source code

```bash
./monailabel/scripts/monailabel start_server \  
  -a apps/radiology \
  -s http://127.0.0.1:8042/dicom-web \
  --conf models deepgrow_2d,localization_spine,localization_vertebra,segmentation_vertebra
```

