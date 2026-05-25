import os, sys, math
from PIL import Image, ImageDraw, ImageFont, ImageText
from chars import Char


class Cell:
    def __init__(self, brightness: int = 0, pixels: Image.Image = Image.new("1", (1, 1))):
        self.brightness = brightness
        self.pixels = pixels


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
    fontName = "CascadiaMono-Regular.ttf"
    font = ImageFont.truetype(f"fonts/{fontName}", fontSize)
    fontDataPath = f"fonts/fontdata-{font.getname()[0]}-{font.getname()[1]}"
    if not os.path.exists(fontDataPath):
        print("Font data file not found, creating font data file...")
        # Save the font data to a file
        with open(fontDataPath, 'w') as f:
            data = ""
            progress = 0
            for c in ascii:
                char = Char(c, 0, Image.new("1", (120, 240)))
                data += f"{char.get_save_data(fontName)}\n"
                progress += 1
                printProgressBar(progress / len(ascii), 50)
            f.write(data)
            print("Font data saved. Initializing characters from file...")
    else:
        print("Font data file found, loading...")
    with open(fontDataPath, 'r') as f:
        for line in f:
            char = line[0]
            newChar = Char(char, 0, Image.new("1", cellSize))
            ImageDraw.Draw(newChar.pixels).text((0, 0), char, font=font, fill=255)
            newChar.brightness = round(float(line[1:]) * (cellSize[0] * cellSize[1]))
            newChar.expand_filter()
            chars.append(newChar)
            printProgressBar((len(chars)) / len(ascii), 50)
    
    # Save images of the characters for debugging purposes
    if test:
        fontTestImage = Image.new("L", (cellSize[0] * len(chars), cellSize[1]))
        for char in chars:
            fontTestImage.paste(char.pixels, (chars.index(char) * cellSize[0], 0))
        fontTestImage.save("test_outputs/font_test_image.png")

    # Check if the target image resolution is a multiple of the cell size, if not round it to the nearest multiple
    image = Image.open(imagePath)
    if image.width % cellSize[0] != 0 or image.height % cellSize[1] != 0:
        newWidth = int(roundToMultiple(image.width, cellSize[0]))
        newHeight = int(roundToMultiple(image.height, cellSize[1]))
        print(f"Image resolution is not a multiple of the cell size, resizing image to {newWidth}x{newHeight}...")
        image = image.resize((newWidth, newHeight))
    
    imageCells = [[Cell() for y in range(image.height // cellSize[1])] for x in range(image.width // cellSize[0])]

    # Apply a custom color quantization filter to the image to reduce the number of colors and make it easier to convert to ASCII art
    print("Quantizing image colors...")
    for x in range(image.width):
        for y in range(image.height):
            printProgressBar((x * image.height + y + 1) / (image.width * image.height), 50)

            pixel = image.getpixel((x, y))
            if len(pixel) == 4:
                pixel = pixel[:3]
            newPixel = []
            for i in range(3):
                newPixel.append(int(roundToMultiple(pixel[i], 255 / colorComplexity)))
            image.putpixel((x, y), tuple(newPixel))
    
    # Save a copy of the quantized image for debugging purposes
    if test:
        image.save("test_outputs/quantized_image.png")

    # Apply an edge detection filter to the image
    print("Applying edge detection filter...")
    filterImage = Image.new("L", image.size)
    for x in range(image.width):
        for y in range(image.height):
            printProgressBar((x * image.height + y + 1) / (image.width * image.height), 50)

            brightness = 0

            if x > 0:
                brightness += 0.5 if image.getpixel((x, y)) != image.getpixel((x - 1, y)) else 0
            if x < image.width - 1:
                brightness += 0.5 if image.getpixel((x, y)) != image.getpixel((x + 1, y)) else 0
            if y > 0:
                brightness += 0.5 if image.getpixel((x, y)) != image.getpixel((x, y - 1)) else 0
            if y < image.height - 1:
                brightness += 0.5 if image.getpixel((x, y)) != image.getpixel((x, y + 1)) else 0
            
            filterImage.putpixel((x, y), round(min(brightness, 1) * 255))

            currentCell = (x // cellSize[0], y // cellSize[1])
            imageCells[currentCell[0]][currentCell[1]].brightness += brightness
            if x % cellSize[0] == cellSize[0] - 1 and y % cellSize[1] == cellSize[1] - 1:
                imageCells[currentCell[0]][currentCell[1]].pixels = filterImage.crop((currentCell[0] * cellSize[0], currentCell[1] * cellSize[1], (currentCell[0] + 1) * cellSize[0], (currentCell[1] + 1) * cellSize[1]))
    
    # Save a copy of the filtered image for debugging purposes
    if test:
        filterImage.save("test_outputs/filtered_image.png")
    
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