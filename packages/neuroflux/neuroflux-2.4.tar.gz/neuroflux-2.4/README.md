# Neuroflux
Neuroflux is a Python package that analyzes MRI and CT scans of brains and highlights regions of tumor damage on a heat map.

## Installation
To install neuroflux, you can use pip:

```
pip install neuroflux
```

The recommended import is:
```
import neuroflux
```

# MRI Scans

## Setup
To begin, declare the following variables:
- case_folder: The folder where the input MRI scans are located (set it to "" if the input files are in the same folder as the program)
- input_flair: The file name of the input FLAIR
- input_t1ce: The file name of the input T1ce
- model_weights: The file name of the predefined model weights

Example setup:
```
case_folder = "BraTS20"
input_flair = "01_flair.nii"
input_t1ce = "01_t1ce.nii"
model_weights = "mri_weights.h5"
```

## Usage
Neuroflux has three main functions:
- prepare_mri_model(model_weights, img_size=128)
    - Creates the U-Net (first step)
- display_slice(folder, input_flair, input_t1ce, slice_num, model, target_layer_name="conv2d_1", img_size=128)
    - Displays the Grad-CAM heat map at a given slice number
- display_grid(folder, input_flair, input_t1ce, model, num_slices=84, rows=7, cols=12, start_slice=20, target_layer_name="conv2d_1")
    - Displays a grid containing a given number of slices beginning at a given slice number

Example usage:
```
model = neuroflux.mri.prepare_mri_model(model_weights=model_weights, img_size=img_size)
neuroflux.mri.display_slice(folder=case_folder, input_flair=input_flair, input_t1ce=input_t1ce, slice_num=77, model=model)
neuroflux.mri.display_grid(folder=case_folder,input_flair=input_flair, input_t1ce=input_t1ce, model=model)
```

# CT Scans

## Setup
To begin, declare the following variables:
- case_folder: The folder where the input CT scans are located (set it to "" if the input files are in the same folder as the program)
- input: The file name of the input CT scan (can be .jpg, .jpeg, or .png)
- model_weights: The file name of the predefined model weights

Example setup:
```
case_folder = "CT Scans"
input = "01.jpg"
model_weights = "ct_weights.pth"
```

## Usage
Neuroflux has three main functions:
- prepare_ct_model(model_weights)
    - Creates the neural network (first step)
- display_gradcam(folder, input, model)
    - Displays the Grad-CAM heat map overlaid on the CT scan

Example usage:
```
model = neuroflux.ct.prepare_ct_model(model_weights=model_weights)
neuroflux.ct.display_gradcam(folder=case_folder, input=input, model=model)
```

# Notes
- The model weights are not built into this package. Our [GitHub](https://github.com/Neuroflux-AI/neuroflux) contains two options to attain model weights for MRI and CT: Use our pre-trained weights (recommended) or run the Google Colab notebook to create your own unique weights.
- To get more involved, see our [website](https://www.neurofluxai.org), read our [research paper](http://doi.org/10.36838/v7i6.64), or contact us at neurofluxai@gmail.com.