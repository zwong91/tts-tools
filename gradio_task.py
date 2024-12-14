import os
import glob
import librosa
import numpy as np
import json
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

# 保存已处理文件到JSON文件
def save_processed_files(processed_files, filename="processed_files.json"):
    with open(filename, 'w') as f:
        json.dump(list(processed_files), f)

# 从JSON文件加载已处理的文件
def load_processed_files(filename="processed_files.json"):
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            return set(json.load(f))
    return set()

# 将文件列表分批，每批最多处理3个
def batch_process(paths, batch_size=3):
    for i in range(0, len(paths), batch_size):
        yield paths[i:i+batch_size]

# 批处理函数，处理多个文件，避免重复处理
def process_files(input_paths):
    # 从文件中加载已处理的文件列表
    processed_files = load_processed_files()

    # 过滤掉已经处理的文件
    files_to_process = [path for path in input_paths if path not in processed_files]

    if not files_to_process:
        print("No new files to process.")
        return

    print(f"Processing: {files_to_process}")
    
    # 1：处理去混响，按批次处理
    for batch in batch_process(files_to_process):
        paths = prepare_paths(batch)
        client = Client("http://127.0.0.1:15555/")
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
        print(f"MDX-Net De-reverb result for {batch}: Success")

        # 2：获取去混响后的主 vocal 路径，并批量处理
        main_vocal_paths = []
        for input_path in batch:
            main_vocal_path = os.path.join('output', 'uvr5_opt', f'{os.path.basename(input_path)}.reformatted.wav_main_vocal.wav')
            
            # 检查输出文件是否有效
            if not is_valid_audio(main_vocal_path):
                print(f"Skipping second model for {input_path} due to invalid output.")
                continue

            main_vocal_paths.append(main_vocal_path)

        if main_vocal_paths:
            # 3：批量处理去回声
            for main_vocal_batch in batch_process(main_vocal_paths):
                paths = prepare_paths(main_vocal_batch)
                client = Client("http://127.0.0.1:15555/")
                result = client.predict(
                    model_name="VR-DeEchoAggressive",
                    inp_root="",
                    save_root_vocal="output/uvr5_opt",
                    paths=paths,  # 批量传递处理后的路径
                    save_root_ins="vc_uvr5_result",
                    agg=10,
                    format0="wav",
                    api_name="/uvr_convert"
                )
                print(f"DeEcho-Aggressive Echo removal result for {main_vocal_batch}: Success")

    # 更新已处理文件列表
    processed_files.update(files_to_process)

    # 保存已处理文件列表
    save_processed_files(processed_files)

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
