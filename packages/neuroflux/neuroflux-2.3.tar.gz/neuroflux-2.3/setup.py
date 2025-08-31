from setuptools import setup, find_packages

with open("README.md", "r") as f:
    long_description = f.read()


setup(
    name="neuroflux",
    version="2.3",
    description="MRI and CT Brain Tumor Diagnosis and Grad-CAM Visualization",
    packages=find_packages(),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Neuroflux-AI/neuroflux",
    install_requires=[
        "matplotlib",
        "numpy",
        "nibabel",
        "opencv-python",
        "Pillow"
        "tensorflow>=2.0",
        "torch",
        "torchvision"
    ],
)