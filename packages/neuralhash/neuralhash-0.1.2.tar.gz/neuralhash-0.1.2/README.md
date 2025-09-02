# Python NeuralHash

This is a library that exposes the [Apple Neuralhash](https://www.apple.com/child-safety/pdf/CSAM_Detection_Technical_Summary.pdf) model, which can be used to determine similar images, even if the images are not exactly the same.

## Installation

From pip:

```bash
pip install neuralhash
```

From source:

```bash
git clone https://github.com/joshterrill/python-neuralhash.git
cd neuralhash
pip install -e .
```

## Usage

Python API:

```python
from neuralhash import get_neuralhash_hex

hash_value = get_neuralhash_hex("tests/sample.png")
print(hash_value)
# ab13fcd08dd3b0a31b07fa2e
```

CLI:

After installation, you also get a command-line tool:

```bash
neuralhash path/to/image.png
# path/to/image.png: a0cca3edec8339d006068f1d
```

Hash multiple files at once:

```bash
neuralhash image1.png image2.jpg
# image1.png: a0cca3edec8339d006068f1d
# image2.png: ab13fcd08dd3b0a31b07fa2e
```

## License

MIT