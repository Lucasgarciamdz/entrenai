# BitNet.cpp Integration Instructions

## 1. Clone and Build BitNet

```sh
git clone --recursive https://github.com/microsoft/BitNet.git
cd BitNet
pip install -r requirements.txt
pip install huggingface_hub
huggingface-cli download microsoft/BitNet-b1.58-2B-4T-gguf --local-dir models/BitNet-b1.58-2B-4T
python setup_env.py -md models/BitNet-b1.58-2B-4T -q i2_s
```

- Place the `BitNet` directory at the root of your project or adjust the path in `bitnet_wrapper.py`.

## 2. Use in Your Python Code

```python
from bitnet_wrapper import run_bitnet_inference

response = run_bitnet_inference("You are a helpful assistant", n_predict=50)
print(response)
```

- The wrapper will call the BitNet C++ backend via subprocess and return the output.
- Make sure the model and BitNet repo are present as described.

## 3. Troubleshooting
- If you see a FileNotFoundError, check that the model is downloaded and paths are correct.
- If you see a RuntimeError, check the stderr for clues (missing dependencies, etc).

## 4. Requirements
- Python 3.9+
- BitNet repo and model as above
- CMake, Clang (for building BitNet if needed)
