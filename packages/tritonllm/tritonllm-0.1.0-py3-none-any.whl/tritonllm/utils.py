import urllib.request
import os
import sys
from tritonllm import gpt_oss, triton_kernels
from pathlib import Path
from typing import Any, Optional, Union
import tempfile
import hashlib
import filelock
import triton
import triton.language as tl


def open_url(url):
    user_agent = 'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/119.0'
    headers = {
        'User-Agent': user_agent,
    }
    request = urllib.request.Request(url, None, headers)
    # Set timeout to 300 seconds to prevent the request from hanging forever.
    return urllib.request.urlopen(request, timeout=300)


def save_file_to_tritonllm_bin_dir(tritonllm_bin_dir):
    os.makedirs(tritonllm_bin_dir, exist_ok=True)
    url = "https://tritonllm.top/down/o200k_base.tiktoken"
    save_as = os.path.join(tritonllm_bin_dir, "fb374d419588a4632f3f557e76b4b70aebbca790")
    if not os.path.exists(save_as):
        with open_url(url) as response:
            content = response.read()

        with open(save_as, "wb") as f:
            f.write(content)

temp_dir = tempfile.gettempdir()

def get_lock(model_name_or_path: Union[str, Path],
             cache_dir: Optional[str] = None):
    lock_dir = cache_dir or temp_dir
    model_name_or_path = str(model_name_or_path)
    os.makedirs(os.path.dirname(lock_dir), exist_ok=True)
    model_name = model_name_or_path.replace("/", "-")
    hash_name = hashlib.sha256(model_name.encode()).hexdigest()
    # add hash to avoid conflict with old users' lock files
    lock_file_name = hash_name + model_name + ".lock"
    # mode 0o666 is required for the filelock to be shared across users
    lock = filelock.FileLock(os.path.join(lock_dir, lock_file_name),
                             mode=0o666)
    return lock


def get_model(size_str) -> str:
    from modelscope import snapshot_download
    pretrained_model_name_or_path = f"openai-mirror/gpt-oss-{size_str}"
    # Use file lock to prevent multiple processes from
    # downloading the same model weights at the same time.
    with get_lock(pretrained_model_name_or_path):
        model_path = snapshot_download(
            model_id=pretrained_model_name_or_path,
            allow_patterns=["original/*"],
        )
        return os.path.join(model_path, "original")


def get_model_with_checkpoint(checkpoint):
    if os.path.exists(checkpoint) and os.path.isdir(checkpoint) and any(
        f.endswith(".safetensors") and os.path.isfile(os.path.join(checkpoint, f))
        for f in os.listdir(checkpoint)
    ):
        return checkpoint
    if checkpoint == "":
        return get_model("20b")
    return get_model(checkpoint)


def init_env():
    tritonllm_bin_dir = os.path.join(Path(gpt_oss.__file__).parent.parent, "bin")

    sys.modules['triton_kernels'] = triton_kernels
    sys.modules['gpt_oss'] = gpt_oss

    os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"
    # os.environ["TIKTOKEN_CACHE_DIR"] = tritonllm_bin_dir

    # download o200k_base.tiktoken
    # save_file_to_tritonllm_bin_dir(tritonllm_bin_dir)


@tl.constexpr_function
def cuda_capability_eq(major, minor=0):
    """
    Determines whether we have compute capability == (major, minor) and
    returns this as a constexpr boolean. This can be used for guarding
    inline asm implementations that require a certain compute capability.
    """
    target = triton.runtime.driver.active.get_current_target()
    if target is None or target.backend != "cuda":
        return False
    assert isinstance(target.arch, int)
    return target.arch == major * 10 + minor


def reduce_block_n(block_n, block_m):
    if cuda_capability_eq(8, 6):
        return block_n // 2
    if cuda_capability_eq(12) and block_n == 256 and block_m == 16:
        return block_n // 2
    return block_n


def reduce_block_k(block_k):
    if cuda_capability_eq(8, 6):
        return block_k // 2
    if cuda_capability_eq(8, 9):
        return block_k // 2
    return block_k
