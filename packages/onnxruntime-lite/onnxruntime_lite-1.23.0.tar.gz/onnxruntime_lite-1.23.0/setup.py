from setuptools import setup, find_packages

setup(
    name="onnxruntime-lite",
    version="1.23.0",
    description="Lightweight ONNX Runtime fork (12MB) for serverless environments",
    author="JacquieAM",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "onnxruntime.capi": ["*.so"],
    },
    python_requires=">=3.12",
    license="Apache 2.0",
    classifiers=[
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
