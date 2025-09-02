import numpy as np
from PIL import Image
import onnxruntime as ort
import importlib.resources as pkg_resources

import neuralhash

_MODEL_PATH = pkg_resources.files(neuralhash).joinpath("model.onnx")
_SEED_PATH = pkg_resources.files(neuralhash).joinpath("neuralhash_128x96_seed1.dat")

_session = ort.InferenceSession(str(_MODEL_PATH), providers=["CPUExecutionProvider"])

# Load seed
with open(_SEED_PATH, "rb") as f:
    seed = np.frombuffer(f.read()[128:], dtype=np.float32).reshape((96, 128))


def get_neuralhash_hex(image_path: str) -> str:
    """
    Compute NeuralHash (hex string) for a given image file.

    Args:
        image_path (str): Path to image file.

    Returns:
        str: NeuralHash value in hex.
    """
    img = Image.open(image_path).convert("RGB").resize((360, 360))
    img_array = np.array(img).astype(np.float32) / 255.0
    img_array = img_array * 2.0 - 1.0
    img_array = img_array.transpose(2, 0, 1).reshape(1, 3, 360, 360)

    input_name = _session.get_inputs()[0].name
    output = _session.run(None, {input_name: img_array})[0]

    logits = output.flatten()
    with np.errstate(all="ignore"):
      projection = seed @ logits

    hash_bits = "".join("1" if x >= 0 else "0" for x in projection)
    hash_hex = f"{int(hash_bits, 2):0{len(hash_bits)//4}x}"

    return hash_hex
