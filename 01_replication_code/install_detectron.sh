#!/bin/bash

python3 -m venv env
source env/bin/activate

pip install wheel
pip install pandas
pip install opencv-python
pip install torch==1.8.0+cpu torchvision==0.9.0+cpu torchaudio==0.8.0 \
  -f https://download.pytorch.org/whl/torch_stable.html
python -m pip install detectron2 -f \
  https://dl.fbaipublicfiles.com/detectron2/wheels/cpu/torch1.8/index.html

python -m pip install dvt
python -m pip install tensorflow keras mtcnn
