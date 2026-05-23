import os, sys, math
from PIL import Image, ImageDraw, ImageFont, ImageText


class Char:
    def __init__(self, char: str, brightness: int, pixels: Image.Image):
        self.char = char
        self.brightness = brightness
        self.pixels = pixels
        self.subCells = [[0 for y in range(12)] for x in range(6)]
    
    def __repr__(self):
        # Return a string with the character, its average brightness, and the average brightness of each subcell
        return f"{self.char}{self.brightness / (self.pixels.size[0] * self.pixels.size[1])},{','.join([str(self.subCells[x][y] / (self.pixels.size[0] * self.pixels.size[1] / 72)) for x in range(6) for y in range(12)])}"


class Cell:
    def __init__(self, brightness: int = 0, pixels: Image.Image = Image.new("1", (1, 1))):
        self.brightness = brightness
        self.pixels = pixels
        self.subCells = [[0 for y in range(12)] for x in range(6)]


def roundToMultiple(value: int|float, multiple: int|float) -> int|float:
    return round(value / multiple) * multiple


def printProgressBar(progress: float, length: int):
    if progress < 1.0:
        print("\r[" + "■" * math.floor(progress * length) + "-" * (length - math.floor(progress * length)) + "]", end="")
    else:
        print("\r[" + "■" * length + "] √")


def main():
    test = False
    if sys.argv[1:] and sys.argv[1] == "--test":
        test = True

    # Get image name from user and confirm it exists in the Images folder
    print("Enter the name of the image you want to convert to ASCII art (must be in the Images folder):")
    imagePath = f"images/{input(':')}"
    while not os.path.exists(imagePath):
        print("Image not found. Name must include file extension (e.g. .jpg, .png) and image must be in the Images folder.")
        imagePath = f"images/{input(':')}"

    # Get font size
    print("Enter the font size, in pixels, higher values result in a smaller and less detailed output: ")
    fontSize = input(':')
    try:
        fontSize = int(fontSize)
    except ValueError:
        fontSize = 0

    while fontSize <= 0:
        print("Font size must be a positive integer.")
        fontSize = int(input(':'))
        try:
            fontSize = int(fontSize)
        except ValueError:
            fontSize = 0
    
    cellSize = (round(fontSize * 0.6), round(fontSize * 1.2))

    # Get the image color complexity for the edge detection filter, higher values result in a more detailed image, but can also result in more noise
    print("Enter the image color complexity for the edge detection filter (higher values result in more detail but can also result in more noise, 3 recommended):")
    colorComplexity = input(':')
    try:
        colorComplexity = int(colorComplexity)
    except ValueError:
        colorComplexity = 0
    
    while colorComplexity <= 0:
        print("Color complexity must be a positive integer.")
        colorComplexity = int(input(':'))
        try:
            colorComplexity = int(colorComplexity)
        except ValueError:
            colorComplexity = 0

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
        tempFont = ImageFont.truetype("fonts/CascadiaMono-Regular.ttf", 20)
        for char in ascii:
            printProgressBar((len(chars)) / len(ascii), 50)
            newChar = Char(char, 0, Image.new("1", (12, 24)))
            ImageDraw.Draw(newChar.pixels).text((0, 0), char, font=tempFont, fill=255)
            for x in range(newChar.pixels.size[0]):
                for y in range(newChar.pixels.size[1]):
                    pixel = newChar.pixels.getpixel((x, y))
                    if pixel > 0:
                        newChar.brightness += 1
                        newChar.subCells[x // round(newChar.pixels.size[0] / 6)][y // round(newChar.pixels.size[1] / 12)] += 1
            chars.append(newChar)
            printProgressBar((len(chars)) / len(ascii), 50)
        
        # Save the font data to a file
        with open(fontDataPath, 'w') as f:
            data = ""
            for char in chars:
                data += f"{char}\n"
            f.write(data)
            print("Font data saved.")
    else:
        print("Font data file found, loading font data...")
    with open(fontDataPath, 'r') as f:
        for line in f:
            char = line[0]
            newChar = Char(char, 0, Image.new("1", cellSize))
            ImageDraw.Draw(newChar.pixels).text((0, 0), char, font=font, fill=255)
            floats = line[1:].split(',')
            newChar.brightness = round(float(floats[0]) * (cellSize[0] * cellSize[1]))
            for x in range(6):
                for y in range(12):
                    newChar.subCells[x][y] = round(float(floats[1 + x * 12 + y]) * (cellSize[0] * cellSize[1] / 72))
            chars.append(newChar)
    
    # Check if the target image resolution is a multiple of the cell size, if not round it to the nearest multiple
    image = Image.open(imagePath)
    if image.size[0] % cellSize[0] != 0 or image.size[1] % cellSize[1] != 0:
        newWidth = int(roundToMultiple(image.size[0], cellSize[0]))
        newHeight = int(roundToMultiple(image.size[1], cellSize[1]))
        print(f"Image resolution is not a multiple of the cell size, resizing image to {newWidth}x{newHeight}...")
        image = image.resize((newWidth, newHeight))
    
    imageCells = [[Cell() for y in range(image.size[1] // cellSize[1])] for x in range(image.size[0] // cellSize[0])]

    # Apply a custom color quantization filter to the image to reduce the number of colors and make it easier to convert to ASCII art
    print("Quantizing image colors...")
    for x in range(image.size[0]):
        for y in range(image.size[1]):
            printProgressBar((x * image.size[1] + y + 1) / (image.size[0] * image.size[1]), 50)

            pixel = image.getpixel((x, y))
            if len(pixel) == 4:
                pixel = pixel[:3]
            newPixel = []
            for i in range(3):
                newPixel.append(int(roundToMultiple(pixel[i], 255 / colorComplexity)))
            image.putpixel((x, y), tuple(newPixel))
    
    # Save a copy of the quantized image for debugging purposes
    if test:
        image.save("test_output_quantized_image.png")

    # Apply an edge detection filter to the image
    print("Applying edge detection filter...")
    filterImage = Image.new("L", image.size)
    for x in range(image.size[0]):
        for y in range(image.size[1]):
            printProgressBar((x * image.size[1] + y + 1) / (image.size[0] * image.size[1]), 50)

            brightness = 0

            if x > 0:
                brightness += 0.5 if image.getpixel((x, y)) != image.getpixel((x - 1, y)) else 0
            if x < image.size[0] - 1:
                brightness += 0.5 if image.getpixel((x, y)) != image.getpixel((x + 1, y)) else 0
            if y > 0:
                brightness += 0.5 if image.getpixel((x, y)) != image.getpixel((x, y - 1)) else 0
            if y < image.size[1] - 1:
                brightness += 0.5 if image.getpixel((x, y)) != image.getpixel((x, y + 1)) else 0
            
            filterImage.putpixel((x, y), round(min(brightness, 1) * 255))

            currentCell = (x // cellSize[0], y // cellSize[1])
            imageCells[currentCell[0]][currentCell[1]].brightness += brightness
            if x % cellSize[0] == cellSize[0] - 1 and y % cellSize[1] == cellSize[1] - 1:
                imageCells[currentCell[0]][currentCell[1]].pixels = filterImage.crop((currentCell[0] * cellSize[0], currentCell[1] * cellSize[1], (currentCell[0] + 1) * cellSize[0], (currentCell[1] + 1) * cellSize[1]))
    
    # Save a copy of the filtered image for debugging purposes
    if test:
        filterImage.save("test_output_filtered_image.png")
    
    # Convert the image cells to ASCII characters
    print("Beginning conversion...")
    output = []
    for y in range(len(imageCells[0])):
        output.append("░" * len(imageCells))
    
    for y in range(len(imageCells[0])):
        for x in range(len(imageCells)):
            cell = imageCells[x][y]
            closestDiff = float("inf")
            closestChar = " "
            for char in chars:
                if abs(cell.brightness - char.brightness) > closestDiff:
                    continue
                charDiff = 0
                for i in range(len(cell.pixels.get_flattened_data())):
                    charDiff += abs(cell.pixels.get_flattened_data()[i] - char.pixels.get_flattened_data()[i]) / 255
                    if charDiff > closestDiff:
                        break
                    elif i == len(cell.pixels.get_flattened_data()) - 1:
                        closestDiff = charDiff
                        closestChar = char.char
                print("\r" + output[y][:x] + closestChar + output[y][x + 1:], end="")
            output[y] = output[y][:x] + closestChar + output[y][x + 1:]
            print("\r" + output[y], end="")
        print("\r" + output[y])
    
    print("Conversion complete. Save output to a text file? (y/n)")
    if input(':').lower() == 'y':
        with open("output.txt", 'w') as f:
            f.write("\n".join(output))
        print("Output saved to output.txt.")
        sys.exit(0)
    else:
        print("Output not saved.")
        sys.exit(0)


if __name__ == "__main__":
    main()