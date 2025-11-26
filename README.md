# image-quantizer
# Advanced Octree Image Quantizer

An advanced **Octree-based image color quantizer** implemented in Python. This project reduces the number of colors in an image while preserving visual quality, making it especially useful for **GIF generation**, **image compression**, and **low-color-depth rendering**.

The implementation is inspired by classic octree color quantization techniques widely used in early computer graphics and modern image formats.

---

## Features

* Efficient **Octree color quantization** algorithm
* Supports configurable **maximum color palette size** (e.g. 256 colors)
* Works with **24-bit RGB images**
* Produces visually accurate low-color outputs
* Clean and extensible Python implementation
* Suitable for research, learning, and production-level preprocessing

---

## Background

Octree color quantization is a tree-based algorithm that clusters image colors into a limited palette. Historically, it was used on hardware with limited color support, and today it is commonly applied when generating **GIFs** or reducing image size.

This implementation builds an octree where each node represents a region in RGB color space. Colors are inserted pixel by pixel, reduced when necessary, and averaged to generate the final palette.

This project is conceptually based on the well-known octree quantizer described here:

* [https://github.com/delimitry/octree_color_quantizer](https://github.com/delimitry/octree_color_quantizer)

---

## How the Algorithm Works

### 1. Octree Structure

An **octree** is a tree where each node has up to **8 children**, corresponding to subdivisions of RGB color space.

* Each level represents one bit of the RGB channels
* A node becomes a **leaf** when it has no active children
* Each leaf stores:

  * Sum of R, G, B values
  * Number of pixels that map to this leaf (`pixel_count`)

---

### 2. Adding Colors to the Octree

For each pixel in the image:

1. Start at the root (level 0)
2. Convert RGB values to binary
3. At each level, select a child index using the current most-significant bit:

```
index = (R_bit << 2) | (G_bit << 1) | B_bit
```

4. Traverse or create child nodes until the maximum depth is reached
5. At the leaf node:

   * Add R, G, B values to the stored sums
   * Increment `pixel_count`

If the same color is added multiple times, its values accumulate, allowing precise averaging later.

---

### 3. Tree Reduction

To limit the palette to a maximum number of colors (e.g. 256):

* While the number of leaf nodes exceeds the allowed palette size:

  * Select reducible parent nodes
  * Merge their children into the parent
  * Sum all child color values and pixel counts
  * Mark the parent as a leaf

This reduction process preserves frequently used colors while merging less significant ones.

**Note:**
In rare worst-case scenarios, the palette may contain slightly fewer colors than requested (e.g. 248 instead of 256) due to the nature of octree merging.

---

### 4. Palette Construction

Once the leaf count is within limits:

For each leaf node:

```
average_color = (
    R_sum / pixel_count,
    G_sum / pixel_count,
    B_sum / pixel_count
)
```

These averaged colors form the final image palette.

---

Dependencies typically include:

* Python 3.8+
* Pillow
* NumPy

---

## Usage

Example usage (simplified):

```python
from quantizer import OctreeQuantizer
from PIL import Image

image = Image.open("input.png")
quantizer = OctreeQuantizer(max_colors=256)

quantized_image = quantizer.quantize(image)
quantized_image.save("output.png")
```

---

## Use Cases

* GIF generation
* Image compression pipelines
* Low-bandwidth image delivery
* Computer graphics research
* Learning classic graphics algorithms

---

## Limitations

* Best suited for RGB images
* Palette size is approximate in rare edge cases
* Not designed for real-time video processing

---

## Future Improvements

* Faster reduction strategy
* Support for RGBA images
* Dithering support
* Parallel processing for large images

---

## Acknowledgements

* Original octree quantization ideas from early computer graphics research
* Inspired by implementations such as:

  * [https://github.com/delimitry/octree_color_quantizer](https://github.com/delimitry/octree_color_quantizer)

---

If you find this project useful, consider starring the repository or contributing improvements.
