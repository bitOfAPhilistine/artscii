import os, sys
from PIL import Image # pyright: ignore[reportMissingImports]


if len(sys.argv) != 2:
    print("Usage: python main.py <image_filename>")
    sys.exit(1)

fontSize = (10, 20)
imagePath = f"Images/{sys.argv[1]}"


def main():
    try:
        with Image.open(imagePath) as im:
            match im.format:
                case "JPEG":
                    im.save("test_output.jpg", "JPEG")
                case "PNG":
                    im.save("test_output.png", "PNG")
    except OSError:
        print("cannot create test image copy")

main()