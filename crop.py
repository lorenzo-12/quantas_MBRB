from PIL import Image
import argparse
import sys

def crop_image(input_path, top, bottom, left, right):
    # Open image
    img = Image.open(input_path)
    width, height = img.size

    # Define crop box: (left, top, right, bottom)
    crop_box = (left, top, width - right, height - bottom)

    # Crop and save
    cropped = img.crop(crop_box)
    cropped.save(input_path)

def main():
    parser = argparse.ArgumentParser(description="Crop parts of an image by specified numbers of pixels from each side.")
    parser.add_argument("input_path", type=str, help="Path to the input image")
    parser.add_argument("--top", type=int, default=0, help="Number of pixels to remove from the top")
    parser.add_argument("--bottom", type=int, default=0, help="Number of pixels to remove from the bottom")
    parser.add_argument("--left", type=int, default=0, help="Number of pixels to remove from the left")
    parser.add_argument("--right", type=int, default=0, help="Number of pixels to remove from the right")
    args = parser.parse_args()

    crop_image(args.input_path, args.top, args.bottom, args.left, args.right)

if __name__ == "__main__":
    main()


# python crop.py input_img --top x --left y --bottom z --right w