#!/bin/bash
conda install -c conda-forge gcc
conda install -c conda-forge gxx
conda install ffmpeg cmake
conda install pytorch==2.2.1 torchvision==0.16.1 torchaudio==2.2.1 pytorch-cuda=12.2 -c pytorch -c nvidia
pip install -r requirements.txt
