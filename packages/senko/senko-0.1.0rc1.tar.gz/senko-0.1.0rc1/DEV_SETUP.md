# Senko Development Setup Guide
## Pre-requisites
- `clang` if on Linux or WSL
    - `sudo apt update; sudo apt install clang`
- `git`
    - `sudo apt update; sudo apt install git` on Linux/WSL
    - On macOS, should already have it if you have the Xcode Command Line Tools installed
- [`uv`](https://docs.astral.sh/uv/#installation)

## Development Setup Steps
First create and activate a Python virtual environment
```
uv venv --python 3.11.13 .venv
source .venv/bin/activate
```
Clone the Senko repository
```
git clone https://github.com/narcotic-sh/senko.git
```
Then install using editable mode (`-e`)
```bash
# For NVIDIA GPUs with CUDA compute capability >= 7.5 (~GTX 16 series and newer)
uv pip install -e "/path/to/cloned/senko[nvidia]"

# For NVIDIA GPUs with CUDA compute capability < 7.5 (~GTX 10 series and older)
uv pip install -e "/path/to/cloned/senko[nvidia-old]"

# For Macs (mps) and cpu execution on all other platforms
uv pip install -e "/path/to/cloned/senko"
```
For NVIDIA, make sure the installed driver is CUDA 12 capable (should see `CUDA Version: 12.x` in the top right of `nvidia-smi`)

Now you can modify the Senko code in the cloned repository folder; changes will be reflected immediately.

Use Senko like normal in scripts:
```python
from senko import Diarizer
import json

diarizer = Diarizer(torch_device='auto', warmup=True, quiet=False)
result = diarizer.diarize('audio.wav', generate_colors=False) # 16 KHz mono wav

with open('./audio_diarized.json', 'w') as f:
    json.dump(result["merged_segments"], f, indent=2)
```
Also see `examples/diarize.py`.
