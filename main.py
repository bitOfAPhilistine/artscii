import os, sys, math
from PIL import Image, ImageDraw, ImageFont, ImageText


class Char:
    def __init__(self, char: str, brightness: int, pixels: Image.Image):
        self.char = char
        self.brightness = brightness
        self.pixels = pixels
    
    def __repr__(self):
        return f"{self.char}{self.brightness / (self.pixels.size[0] * self.pixels.size[1])}"


def roundToMultiple(value: int|float, multiple: int|float) -> int|float:
    return round(value / multiple) * multiple


def main():
    # Get image name from user and confirm it exists in the Images folder
    print("Enter the name of the image you want to convert to ASCII art (must be in the Images folder):")
    imagePath = f"images/{input('')}"
    while not os.path.exists(imagePath) and imagePath != "images/test":
        print("Image not found. Name must include file extension (e.g. .jpg, .png) and image must be in the Images folder.")
        imagePath = f"images/{input('')}"

    # Get font size
    print("Enter the font size, in pixels, higher values result in less detail: ")
    fontSize = input('')
    try:
        fontSize = int(fontSize)
    except ValueError:
        fontSize = 0

    while fontSize <= 0:
        print("Font size must be a positive integer.")
        fontSize = int(input(''))
        try:
            fontSize = int(fontSize)
        except ValueError:
            fontSize = 0
    
    cellSize = (int(fontSize * 0.6), int(fontSize * 1.2))

    ascii = '''
☺☻♥♦♣♠•◘○◙♂♀♪♫☼►◄↕‼¶§▬↨↑↓→←∟↔▲▼ 
!"#$%&'()*+,-./0123456789:;<=>?@
ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`
abcdefghijklmnopqrstuvwxyz{|}~∙·
ÇüéâäàåçêëèïîìÄÅÉæÆôöòûùÿÖÜø£Ø₧ƒ
áíóúñÑªº¿®¬½¼¡«»░▒▓│┤ÁÂÀ©╣║╗╝¢¥┐
└┴┬├─┼ãÃ╚╔╩╦╠═╬¤ðÐÊËÈıÍÎÏ┘┌█▄▌▐▀
αßΓπΣσµτΦΘΩδ∞φε∩≡±≥≤⌠⌡÷≈°√ⁿ²■'''
    ascii = ascii.replace('\n', '')
    chars = []

    # Check for a font data file in the fonts folder and create one if it doesn't exist
    font = ImageFont.truetype("fonts/CascadiaMono-Regular.ttf", fontSize)
    fontDataPath = f"fonts/fontdata-{font.getname()[0]}-{font.getname()[1]}"
    if not os.path.exists(fontDataPath):
        print("Font data file not found, creating font data file...")
        # initialize the chars list with an image for each character and calculate the brightness of each character
        for char in ascii:
            newChar = Char(char, 0, Image.new("1", cellSize))
            ImageDraw.Draw(newChar.pixels).text((0, 0), char, font=font, fill=255)
            for pixel in newChar.pixels.get_flattened_data():
                newChar.brightness += pixel
            chars.append(newChar)
        
        # Save the font data to a file
        with open(fontDataPath, 'w') as f:
            data = ""
            for char in chars:
                data += f"{char}\n"
            f.write(data)
    else:
        print("Font data file found, loading font data...")
        with open(fontDataPath, 'r') as f:
            for line in f:
                char = line[0]
                newChar = Char(char, 0, Image.new("1", cellSize))
                ImageDraw.Draw(newChar.pixels).text((0, 0), char, font=font, fill=255)
                newChar.brightness = round(float(line[1:]) * (cellSize[0] * cellSize[1]))
                chars.append(newChar)
    
    # Check if the target image resolution is a multiple of the cell size, if not round it to the nearest multiple
    image = Image.open(imagePath)
    if image.size[0] % cellSize[0] != 0 or image.size[1] % cellSize[1] != 0:
        newWidth = int(roundToMultiple(image.size[0], cellSize[0]))
        newHeight = int(roundToMultiple(image.size[1], cellSize[1]))
        print(f"Image resolution is not a multiple of the cell size, resizing image to {newWidth}x{newHeight}...")
        image = image.resize((newWidth, newHeight))
    
    # Apply an edge detection filter to the image
    imageCellsBrightness = []
    filterImage = Image.new("L", image.size)
    isColorImage = len(image.getbands()) > 1
    for x in range(image.size[0]):
        for y in range(image.size[1]):
            brightness = 0

            if x > 0:
                if isColorImage:
                    brightness += sum([abs(image.getpixel((x, y))[i] - image.getpixel((x - 1, y))[i]) for i in range(3)]) / 3
                else:
                    brightness += abs(image.getpixel((x, y)) - image.getpixel((x - 1, y)))
            if x < image.size[0] - 1:
                if isColorImage:
                    brightness += sum([abs(image.getpixel((x, y))[i] - image.getpixel((x + 1, y))[i]) for i in range(3)]) / 3
                else:
                    brightness += abs(image.getpixel((x, y)) - image.getpixel((x + 1, y)))
            if y > 0:
                if isColorImage:
                    brightness += sum([abs(image.getpixel((x, y))[i] - image.getpixel((x, y - 1))[i]) for i in range(3)]) / 3
                else:
                    brightness += abs(image.getpixel((x, y)) - image.getpixel((x, y - 1)))
            if y < image.size[1] - 1:
                if isColorImage:
                    brightness += sum([abs(image.getpixel((x, y))[i] - image.getpixel((x, y + 1))[i]) for i in range(3)]) / 3
                else:
                    brightness += abs(image.getpixel((x, y)) - image.getpixel((x, y + 1)))
            
            filterImage.putpixel((x, y), int(brightness))

            currentCell = (x // cellSize[0], y // cellSize[1])
            if len(imageCellsBrightness) <= currentCell[0]:
                imageCellsBrightness.append([])
            imageCellsBrightness[currentCell[0]].append(brightness)
    # save a copy of the filtered image for debugging purposes
    filterImage.save("test_output_filtered_image.png")


if __name__ == "__main__":
    main()