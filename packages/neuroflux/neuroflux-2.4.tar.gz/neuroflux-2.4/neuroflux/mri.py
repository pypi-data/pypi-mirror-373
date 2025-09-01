import os
import numpy as np
import nibabel as nib
import cv2
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Conv2D, MaxPooling2D, UpSampling2D, Dropout, concatenate

CLASS_NAMES = {1: "Necrotic core", 2: "Edema", 3: "Enhancing tumor"}

def build_unet(input_layer, ker_init="he_normal", dropout=0.2):
    conv1 = Conv2D(32, 3, activation='relu', padding='same', kernel_initializer=ker_init)(input_layer)
    conv1 = Conv2D(32, 3, activation='relu', padding='same', kernel_initializer=ker_init)(conv1)

    pool = MaxPooling2D()(conv1)
    conv = Conv2D(64, 3, activation='relu', padding='same', kernel_initializer=ker_init)(pool)
    conv = Conv2D(64, 3, activation='relu', padding='same', kernel_initializer=ker_init)(conv)

    pool1 = MaxPooling2D()(conv)
    conv2 = Conv2D(128, 3, activation='relu', padding='same', kernel_initializer=ker_init)(pool1)
    conv2 = Conv2D(128, 3, activation='relu', padding='same', kernel_initializer=ker_init)(conv2)

    pool2 = MaxPooling2D()(conv2)
    conv3 = Conv2D(256, 3, activation='relu', padding='same', kernel_initializer=ker_init)(pool2)
    conv3 = Conv2D(256, 3, activation='relu', padding='same', kernel_initializer=ker_init)(conv3)

    pool4 = MaxPooling2D()(conv3)
    conv5 = Conv2D(512, 3, activation='relu', padding='same', kernel_initializer=ker_init)(pool4)
    conv5 = Conv2D(512, 3, activation='relu', padding='same', kernel_initializer=ker_init)(conv5)
    drop5 = Dropout(dropout)(conv5)

    up7 = Conv2D(256, 2, activation='relu', padding='same', kernel_initializer=ker_init)(UpSampling2D()(drop5))
    merge7 = concatenate([conv3, up7])
    conv7 = Conv2D(256, 3, activation='relu', padding='same', kernel_initializer=ker_init)(merge7)
    conv7 = Conv2D(256, 3, activation='relu', padding='same', kernel_initializer=ker_init)(conv7)

    up8 = Conv2D(128, 2, activation='relu', padding='same', kernel_initializer=ker_init)(UpSampling2D()(conv7))
    merge8 = concatenate([conv2, up8])
    conv8 = Conv2D(128, 3, activation='relu', padding='same', kernel_initializer=ker_init)(merge8)
    conv8 = Conv2D(128, 3, activation='relu', padding='same', kernel_initializer=ker_init)(conv8)

    up9 = Conv2D(64, 2, activation='relu', padding='same', kernel_initializer=ker_init)(UpSampling2D()(conv8))
    merge9 = concatenate([conv, up9])
    conv9 = Conv2D(64, 3, activation='relu', padding='same', kernel_initializer=ker_init)(merge9)
    conv9 = Conv2D(64, 3, activation='relu', padding='same', kernel_initializer=ker_init)(conv9)

    up = Conv2D(32, 2, activation='relu', padding='same', kernel_initializer=ker_init)(UpSampling2D()(conv9))
    merge = concatenate([conv1, up])
    conv = Conv2D(32, 3, activation='relu', padding='same', kernel_initializer=ker_init)(merge)
    conv = Conv2D(32, 3, activation='relu', padding='same', kernel_initializer=ker_init)(conv)

    conv10 = Conv2D(4, (1, 1), activation='softmax')(conv)
    return Model(inputs=input_layer, outputs=conv10)

def prepare_mri_model(model_weights, img_size=128):
    model = build_unet(Input((img_size, img_size, 2)))
    model.load_weights(model_weights)
    return model

def prepare_input_image(folder, input_flair, input_t1ce, slice_num, img_size=128):
    flair = nib.load(os.path.join(folder, input_flair)).get_fdata()
    t1ce = nib.load(os.path.join(folder, input_t1ce)).get_fdata()

    flair_slice = cv2.resize(flair[:, :, slice_num], (img_size, img_size)) / np.max(flair)
    t1ce_slice = cv2.resize(t1ce[:, :, slice_num], (img_size, img_size)) / np.max(t1ce)

    input_img = np.stack([flair_slice, t1ce_slice], axis=-1)
    return np.expand_dims(input_img.astype(np.float32), axis=0)

def get_main_tumor_class(prediction_mask):
    flat = prediction_mask.flatten()
    unique, counts = np.unique(flat, return_counts=True)
    class_counts = dict(zip(unique, counts))
    class_counts.pop(0, None)

    if not class_counts:
        return None

    return max(class_counts, key=class_counts.get)

def get_gradcam_heatmap(model, input_image, class_index, target_layer_name):
    grad_model = Model(inputs=model.inputs, outputs=[model.get_layer(target_layer_name).output, model.output])
    with tf.GradientTape() as tape:
        conv_output, predictions = grad_model(input_image)
        loss = predictions[..., class_index]

    grads = tape.gradient(loss, conv_output)
    pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))

    conv_output = conv_output[0]
    heatmap = conv_output @ pooled_grads[..., tf.newaxis]
    heatmap = tf.squeeze(heatmap)
    heatmap = tf.maximum(heatmap, 0) / tf.math.reduce_max(heatmap)
    return heatmap.numpy()

def display_slice(folder, input_flair, input_t1ce, slice_num, model, target_layer_name="conv2d_1", img_size=128):
    input_image = prepare_input_image(folder, input_flair, input_t1ce, slice_num)

    flair_path = os.path.join(folder, input_flair)
    t1ce_path = os.path.join(folder, input_t1ce)

    flair = nib.load(flair_path).get_fdata()[:, :, slice_num]
    t1ce = nib.load(t1ce_path).get_fdata()[:, :, slice_num]

    flair_resized = cv2.resize(flair, (img_size, img_size))
    t1ce_resized = cv2.resize(t1ce, (img_size, img_size))

    prediction = model.predict(input_image, verbose=0)[0]
    seg_mask = np.argmax(prediction, axis=-1)

    class_idx = get_main_tumor_class(seg_mask)

    # Plot 3 side-by-side images + Grad-CAM below
    fig, axes = plt.subplots(1, 3, figsize=(12, 8))
    axes = axes.flatten()

    axes[0].imshow(flair_resized, cmap='gray')
    axes[0].set_title('FLAIR')
    axes[0].axis('off')

    axes[1].imshow(t1ce_resized, cmap='gray')
    axes[1].set_title('T1CE')
    axes[1].axis('off')

    axes[2].imshow(seg_mask, cmap='nipy_spectral')
    axes[2].set_title('Predicted Segmentation')
    axes[2].axis('off')

    if class_idx is not None:
        heatmap = get_gradcam_heatmap(model, input_image, class_idx, target_layer_name)
        overlay_img = input_image[0, :, :, 0]
        fig2, ax = plt.subplots(figsize=(6, 6))
        ax.imshow(overlay_img, cmap='gray')
        ax.imshow(heatmap, cmap='jet', alpha=0.5)
        tumor_name = CLASS_NAMES.get(class_idx, f"Class {class_idx}")
        ax.axis('off')
        plt.tight_layout()
        plt.savefig(f"mri_gradcam_slice_{slice_num}.png")
        plt.show()
    else:
        print("No tumor class detected — skipping Grad-CAM.")

def display_grid(folder, input_flair, input_t1ce, model, num_slices=84, rows=7, cols=12, start_slice=20, target_layer_name="conv2d_1"):
    fig, axes = plt.subplots(rows, cols, figsize=(20, 20))
    axes = axes.flatten()

    for i in range(min(num_slices, len(axes))):
        slice_num = i
        input_image = prepare_input_image(folder, input_flair, input_t1ce, slice_num + start_slice)

        prediction = model.predict(input_image, verbose=0)[0]
        pred_mask = np.argmax(prediction, axis=-1)
        class_idx = get_main_tumor_class(pred_mask)

        axes[i].imshow(input_image[0, :, :, 0], cmap="gray")

        if class_idx is None:
            axes[i].set_title(f"Slice {slice_num + start_slice}\nNo tumor found")
        else:
            heatmap = get_gradcam_heatmap(model, input_image, class_idx, target_layer_name)
            axes[i].imshow(heatmap, cmap='jet', alpha=0.5)
            tumor_name = CLASS_NAMES.get(class_idx, f"Class {class_idx}")
            axes[i].set_title(f"Slice {slice_num + start_slice}")

        axes[i].axis("off")

    for ax in axes[num_slices:]:
        ax.axis("off")

    plt.tight_layout()
    plt.savefig("mri_gradcam_grid.png")
    plt.show()