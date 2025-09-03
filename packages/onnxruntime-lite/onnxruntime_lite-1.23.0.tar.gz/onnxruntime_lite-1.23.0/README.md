
# ONNX Runtime Lite (15 MB)

**Ultralight fork of [ONNX Runtime](https://github.com/microsoft/onnxruntime)**, optimized for **resource-constrained environments** such as **AWS Lambda**.

This fork is specialized for:

* **T5 models** (text-to-text generation)
* **Roberta-based classifiers (MiniLM)**

##  Why this fork?

* **Tiny footprint** (~15 MB vs >100 MB official builds)
* **AWS Lambda-ready** (fits within size limits for serverless deployments)
* **Optimized**: stripped of unused ops, kernels, and heavyweight features
* **Plug-and-play**: drop into Python projects with the same `import onnxruntime`

##  Installation


### Install via PYPI (recommended)

The easiest way to install:
```
pip install onnxruntime-lite
```
### Install from GitHub (for development or contributions)

Clone or download:

```bash
git clone https://github.com/JacquieAM/onnxruntime-lite.git
```
Navigate to the cloned folder:

```
cd onnxruntime-lite
```

Then Install via pip :
```
pip install .
```
Use it directly in Python:

```
import onnxruntime as ort
```

# Example: Run a T5 or MiniLM classifier

session = ort.InferenceSession("model.onnx")

# Supported Use Cases

MiniLM (Roberta classifier)

T5 seq2seq models

⚠️ Not a full replacement for standard ONNX Runtime (unsupported ops stripped out)

# Ideal For

AWS Lambda

Serverless environments

Lightweight Docker images

Edge deployments

# Notes

This fork keeps all subfolders necessary for T5 and MiniLM.

The package is deliberately stripped and repackaged to minimize size.

Contributions or further optimizations for other models are welcome.

## License

This fork is based on ONNX Runtime (https://github.com/microsoft/onnxruntime), which is licensed under the MIT License.
