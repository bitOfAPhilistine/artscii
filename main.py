import os, sys, math
from PIL import Image, ImageDraw, ImageFont, ImageText


class Char:
    def __init__(self, char: str, brightness: int, pixels: Image.Image):
        self.char = char
        self.brightness = brightness
        self.pixels = pixels
    
    def __repr__(self):
        return f"Char(char='{self.char}', brightness={self.brightness})"


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
    
    cellSize = (fontSize * 0.6, fontSize * 1.2)

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

    # Check for a font sheet image jpg in the fonts folder and create one if it doesn't exist
    font = ImageFont.truetype("fonts/CascadiaMono-Regular.ttf", 256)
    fontSheetPath = f"fonts/fontsheet_{font.getname()[0]}_{font.getname()[1]}.jpg"
    charSize = (154, 308)
    if not os.path.exists(fontSheetPath): # If the font sheet doesn't exist, create it
        print("Font sheet not found, creating font sheet...")

        # Create a new image to draw the font sheet on
        fontSheet = Image.new("1", (charSize[0] * 32, charSize[1] * 8))
        
        # Generate a sub-image for each character in the ascii string and draw it on the font sheet, then add it to chars
        for i, char in enumerate(ascii):
            x = (i % 32) * charSize[0]
            y = (i // 32) * charSize[1]
            charImage = Image.new("1", (charSize[0], charSize[1]))
            ImageDraw.Draw(charImage).text((0, 0), char, font=font, fill=1)
            fontSheet.paste(charImage, (int(x), int(y)))
            chars.append(Char(char, 0, charImage))
        
        # Save the font sheet image for future use
        fontSheet.save(fontSheetPath)
    else: # If the font sheet already exists, load it and generate the chars list from it
        print("Font sheet found, loading font sheet...")

        fontSheet = Image.open(fontSheetPath)

        for i, char in enumerate(ascii):
            x = (i % 32) * charSize[0]
            y = (i // 32) * charSize[1]
            charImage = fontSheet.crop((x, y, x + charSize[0], y + charSize[1]))
            chars.append(Char(char, 0, charImage))
    
    # Calculate the total brightness of each character
    for char in chars:
        brightness = 0
        for pixel in char.pixels.get_flattened_data():
            brightness += pixel
        char.brightness = brightness
    
    # Check if the target image resolution is a multiple of the cell size, if not round it to the nearest multiple
    image = Image.open(imagePath)
    if image.size[0] % cellSize[0] != 0 or image.size[1] % cellSize[1] != 0:
        newWidth = int(roundToMultiple(image.size[0], cellSize[0]))
        newHeight = int(roundToMultiple(image.size[1], cellSize[1]))
        print(f"Image resolution is not a multiple of the cell size, resizing image to {newWidth}x{newHeight}...")
        image = image.resize((newWidth, newHeight))
    
    # print(chars)

if __name__ == "__main__":
    main()