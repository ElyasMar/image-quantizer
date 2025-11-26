from PIL import Image
from color import Color
from octree_quantizer import OctreeQuantizer


def main():
    print("Loading image...")

    # Load image with error handling
    try:
        image = Image.open('./Image_Input/cat.jpg')
        pixels = image.load()
        width, height = image.size
        print(f"Image loaded: {width}x{height} pixels")
    except Exception as e:
        print(f"Error loading image: {e}")
        return

    # Create octree quantizer
    octree = OctreeQuantizer()
    print("Building octree...")

    # Add colors to the octree with progress tracking
    total_pixels = width * height
    for j in range(height):
        for i in range(width):
            octree.add_color(Color(*pixels[i, j]))

        # Show progress every 10% of rows
        if (j + 1) % max(1, height // 10) == 0:
            progress = ((j + 1) / height) * 100
            print(f"Progress: {progress:.0f}%")

    print(f"Added {total_pixels} pixels to octree")

    # Generate 256 colors for 8 bits per pixel output image
    print("Generating palette...")
    palette = octree.make_palette(256)
    print(f"Generated palette with {len(palette)} colors")

    # Save real image into folder
    image.save('./Output/original/cat.png')
    print('Image saved to: ./Output/original/cat.png')

    # Create and save palette visualization
    print("Creating palette image...")
    palette_image = Image.new('RGB', (16, 16), (0, 0, 0))
    palette_pixels = palette_image.load()

    for i, color in enumerate(palette):
        if i < 256:  # Ensure we don't exceed 16x16 grid
            x, y = i % 16, i // 16
            palette_pixels[x, y] = (color.red, color.green, color.blue)

    palette_image.save('./Output/palette/cat_palette.png')
    print("Palette saved to: ./Output/palette/cat_palette.png")

    # Create and save quantized output image
    print("Creating quantized image...")
    out_image = Image.new('RGB', (width, height))
    out_pixels = out_image.load()

    for j in range(height):
        for i in range(width):
            try:
                index = octree.get_palette_index(Color(*pixels[i, j]))
                if index < len(palette):
                    color = palette[index]
                    out_pixels[i, j] = (color.red, color.green, color.blue)
                else:
                    # Fallback to black if index is out of bounds
                    out_pixels[i, j] = (0, 0, 0)
            except Exception as e:
                # Fallback for any errors
                out_pixels[i, j] = (0, 0, 0)

        # Show progress for output generation
        if (j + 1) % max(1, height // 10) == 0:
            progress = ((j + 1) / height) * 100
            print(f"Output progress: {progress:.0f}%")

    out_image.save('./Output/quantized_image/cat_quantized.png')
    print("Quantized image saved to: ./Output/quantized_image/cat_quantized.png")

    # Show statistics
    stats = octree.get_stats()
    print(f"\nStatistics:")
    print(f"- Total nodes created: {stats['total_nodes']}")
    print(f"- Final leaf nodes: {stats['leaf_count']}")
    print(f"- Colors in palette: {len(palette)}")

    print("\nProcess completed successfully!")


if __name__ == '__main__':
    main()