# Optional: helper functions (e.g., preprocess batch images, caching)
from PIL import Image

def load_image(path):
    return Image.open(path).convert("RGB")
