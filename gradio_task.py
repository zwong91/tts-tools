import os
import glob
import librosa
import numpy as np
from gradio_client import Client, file

# 检查路径是否为 URL
def is_url(path):
    return isinstance(path, str) and (path.startswith("http://") or path.startswith("https://"))

# 处理路径：如果是 URL，使用 file()；如果是本地文件路径，直接传递
def prepare_paths(paths):
    return [file(path) if is_url(path) else path for path in paths]

# 检查音频文件是否有效（无NaN或无穷值）
def is_valid_audio(file_path):
    try:
        audio, sr = librosa.load(file_path, sr=None)
        if np.any(np.isnan(audio)) or np.any(np.isinf(audio)):
            return False
        return True
    except Exception:
        return False

# 批处理函数，处理多个文件
def process_files(input_paths):
    client = Client("http://127.0.0.1:15555/")
    for input_path in input_paths:
        print(f"Processing: {input_path}")
        
        # 第一次调用：处理去混响
        paths = prepare_paths([input_path])
        result = client.predict(
            model_name="onnx_dereverb_By_FoxJoy",
            inp_root="",
            save_root_vocal="output/uvr5_opt",
            paths=paths,
            save_root_ins="output/uvr5_opt",
            agg=10,
            format0="wav",
            api_name="/uvr_convert"
        )
        print(f"De-reverb result for {input_path}: Success")

        # 获取第一次调用的输出文件路径
        main_vocal_path = os.path.join('output', 'uvr5_opt', f'{os.path.basename(input_path)}.reformatted.wav_main_vocal.wav')

        # 检查第一次调用的输出文件是否有效
        if not is_valid_audio(main_vocal_path):
            print(f"Skipping second model for {input_path} due to invalid output.")
            continue
        
        # 第二次调用：去回声
        paths = prepare_paths([main_vocal_path])
        result = client.predict(
            model_name="VR-DeEchoAggressive",
            inp_root="",
            save_root_vocal="output/uvr5_opt",
            paths=[file(path) for path in paths],  # 处理后的路径
            save_root_ins="output/uvr5_opt",
            agg=10,
            format0="wav",
            api_name="/uvr_convert"
        )
        print(f"Echo removal result for {input_path}: Success")

    print("Batch processing complete!")

# 批量获取本地音频文件（支持 .wav, .flac, .mp3, .m4a 格式）
def get_local_audio_files(input_folder):
    input_paths = []
    input_paths.extend(glob.glob(os.path.join(input_folder, "*.wav")))
    input_paths.extend(glob.glob(os.path.join(input_folder, "*.flac")))
    input_paths.extend(glob.glob(os.path.join(input_folder, "*.mp3")))
    input_paths.extend(glob.glob(os.path.join(input_folder, "*.m4a")))
    return input_paths

# 从 URL 或本地文件夹路径创建输入列表
def create_input_paths(input_folder, input_urls):
    local_paths = get_local_audio_files(input_folder)
    all_input_paths = local_paths + input_urls
    return all_input_paths

# URL 列表
input_urls = [
    'https://raw.githubusercontent.com/zwong91/rt-audio/main/vc/liuyifei.wav',
]

# 批量处理函数，指定要处理的本地文件夹路径
input_folder = '/home/ubuntu/front/rt-audio/vc'
input_paths = create_input_paths(input_folder, input_urls)

# 执行批处理
process_files(input_paths)
