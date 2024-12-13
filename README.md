From GPT-SoVITS
---

### Environments

- Python 3.10.13, PyTorch 2.1.1, CUDA 12.2
- Python 3.10.13, PyTorch 2.1.1, macOS 14.4.1 (Apple silicon)

_Note: numba==0.56.4 requires py<3.11_

### Linux
```bash

rm /usr/bin/rclone
rm /usr/local/share/man/man1/rclone.1
wget https://downloads.rclone.org/v1.67.0/rclone-v1.67.0-linux-amd64.zip
apt update 
apt install zip unzip 
unzip rclone-v1.67.0-linux-amd64.zip
cp rclone-v1.67.0-linux-amd64/rclone  /usr/local/bin/
cp rclone-v1.67.0-linux-amd64/rclone /usr/bin/

mkdir -p ~/.config/rclone
cat << EOF > ~/.config/rclone/rclone.conf
[unc_cf]
type = s3
provider = Cloudflare
access_key_id = c51bb3ea6e80fc1cb90beb966d54b6b8
secret_access_key = ed1f8de685f69a9c965759e601d6e637c463ae15d62faded2869f9ef9a6c8baa
endpoint = https://ec9b597fa02615ca6a0e62b7ff35d0cc.r2.cloudflarestorage.com
acl = private
EOF

#从s3 下载
rclone copy --no-check-certificate --progress --transfers=6  unc_cf:models/uvr5_weights.zip  ./

#上传到s3
rclone sync uvr5_weights.zip unc_cf:models/   --progress


# 安装 miniconda, PyTorch/CUDA 的 conda 环境
mkdir -p ~/miniconda3
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda3/miniconda.sh
bash ~/miniconda3/miniconda.sh -b -u -p ~/miniconda3
rm -rf ~/miniconda3/miniconda.sh
~/miniconda3/bin/conda init bash && source ~/miniconda3/bin/activate

conda create -n UVR5 python=3.10 -y
conda activate UVR5
bash install.sh
```

### macOS

**Note: The models trained with GPUs on Macs result in significantly lower quality compared to those trained on other devices, so we are temporarily using CPUs instead.**

1. Install Xcode command-line tools by running `xcode-select --install`.
2. Install FFmpeg by running `brew install ffmpeg`.
3. Install the program by running the following commands:

```bash
conda create -n UVR5 python=3.10
conda activate UVR5
pip install -r requirements.txt
```

### Install Manually

#### Install FFmpeg

##### Conda Users

```bash
conda install ffmpeg
```

##### Ubuntu/Debian Users

```bash
sudo apt install ffmpeg
sudo apt install libsox-dev
conda install -c conda-forge 'ffmpeg<7'
```

##### MacOS Users
```bash
brew install ffmpeg
```

#### Install Dependences

```bash
pip install -r requirements.txt
```

## Pretrained Models

**Users in China can [download all these models here](https://www.yuque.com/baicaigongchang1145haoyuangong/ib3g1e/dkxgpiy9zb96hob4#nVNhX).**

UVR5 (Vocals/Accompaniment Separation & Reverberation Removal, additionally), download models from [UVR5 Weights](https://huggingface.co/lj1995/VoiceConversionWebUI/tree/main/uvr5_weights) and place them in `/uvr5/uvr5_weights`.

1.Fill in the audio path

2.Slice the audio into small chunks

3.Denoise(optinal)

## Method for running from the command line
Use the command line to open the WebUI for UVR5
```
python uvr5/webui.py "<device>" <is_half> <webui_port_uvr5> <is_share>
```
<!-- If you can't open a browser, follow the format below for UVR processing,This is using mdxnet for audio processing
```
python mdxnet.py --model --input_root --output_vocal --output_ins --agg_level --format --device --is_half_precision 
``` -->
This is how the audio segmentation of the dataset is done using the command line
```
python audio_slicer.py \
    --input_path "<path_to_original_audio_file_or_directory>" \
    --output_root "<directory_where_subdivided_audio_clips_will_be_saved>" \
    --threshold <volume_threshold> \
    --min_length <minimum_duration_of_each_subclip> \
    --min_interval <shortest_time_gap_between_adjacent_subclips> 
    --hop_size <step_size_for_computing_volume_curve>

### WebUI Tools
- [ultimatevocalremovergui](https://github.com/Anjok07/ultimatevocalremovergui)
- [audio-slicer](https://github.com/openvpi/audio-slicer)
- [SubFix](https://github.com/cronrpc/SubFix)
- [FFmpeg](https://github.com/FFmpeg/FFmpeg)
- [gradio](https://github.com/gradio-app/gradio)
- [faster-whisper](https://github.com/SYSTRAN/faster-whisper)
- [FunASR](https://github.com/alibaba-damo-academy/FunASR)
