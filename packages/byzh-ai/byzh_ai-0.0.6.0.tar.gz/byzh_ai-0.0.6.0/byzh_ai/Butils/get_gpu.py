import subprocess

def b_get_gpu_nvidia():
    result = subprocess.check_output(
        # nvidia-smi --query-gpu=index,name,memory.used,memory.total,utilization.gpu --format=csv,noheader,nounits
        ["nvidia-smi", "--query-gpu=index,name,memory.used,memory.total,utilization.gpu", "--format=csv,noheader,nounits"],
        encoding='utf-8'
    )
    gpus = []
    for line in result.strip().split('\n'):
        if line:
            gpu_index, gpu_name, memory_used, memory_total, gpu_util = line.split(', ')
            gpus.append([int(gpu_index), gpu_name, float(gpu_util), int(memory_used), int(memory_total)])
    return gpus

if __name__ == '__main__':
    gpus = b_get_gpu_nvidia()
    for gpu in gpus:
        print(gpu)
        # [0, 'NVIDIA GeForce RTX 4090', 32.0, 3854, 24564]
        # [1, 'NVIDIA GeForce RTX 4090', 33.0, 891, 24564]
