import os, sys, math
from PIL import Image, ImageDraw, ImageFont, ImageText


class Char:
    def __init__(self, char: str, font: ImageFont.ImageFont, fontSize: int, index: int | None = None):
        self.char = char
        self.rgbTotals = (0, 0, 0)
        cellSize = (round(fontSize * 0.6), round(fontSize * 1.2))
        self.pixels = Image.new("rgb", cellSize) # r is horizontal bias, g is vertical bias, b is overall brightness

        # Load the character's pixel data from the font file, if index is provided, otherwise generate it
        if index is not None:
            self.load_from_files(index, f"fonts/{font.getname()[0]}-{font.getname()[1]}-{fontSize}")
        else:
            rawPixels = Image.new("1", cellSize)
            ImageDraw.Draw(rawPixels).text((0, 0), char, font=font, fill=255)
            self.init_from_raw(rawPixels)

    def __repr__(self):
        # Return a string with the character, and its rgb totals
        return f"{self.char}{self.rgbTotals[0]},{self.rgbTotals[1]},{self.rgbTotals[2]}"
    
    def init_from_raw(self, rawPixels: Image.Image):
        for x in range(rawPixels.width):
            for y in range(rawPixels.height):
                pixel = rawPixels.getpixel((x, y))
                if pixel > 0:
                    toCheck = ((x + 1, y), (x + 1, y + 1), (x, y + 1), (x - 1, y + 1))
                    rgb = self.pixels.getpixel((x, y))
                    for check in toCheck:
                        if check[0] < 0 or check[0] >= rawPixels.width or check[1] >= rawPixels.height:
                            continue

                        checkPix = self.pixels.getpixel(check)
                        if rawPixels.getpixel(check) > 0:
                            if check[0] == x:
                                rgb[1] += 128
                                checkPix[1] += 128
                                self.pixels.putpixel(check, checkPix)
                            elif check[1] == y:
                                rgb[0] += 128
                                checkPix[0] += 128
                                self.pixels.putpixel(check, checkPix)
                            else:
                                rgb[0] += 64
                                rgb[1] += 64
                                checkPix[0] += 64
                                checkPix[1] += 64
                                self.pixels.putpixel(check, checkPix)
                    self.pixels.putpixel((x, y), rgb)
                    self.rgbTotals = (self.rgbTotals[0] + rgb[0], self.rgbTotals[1] + rgb[1], self.rgbTotals[2] + rgb[2])
    
    def load_from_files(self, index: int, folder: str):
        # Get the character's data from the font data file, and load the character's pixel data from the image file
        with open(f"{folder}/data.txt", 'r') as f:
            data = f.readlines()[index]
            self.rgbTotals = tuple(map(int, data[1:].split(",")))
            # Raise an error if the given data is invalid so the main file can delete the font data file and create a new one
            if self.char != data[0]:
                raise ValueError(f"Character mismatch in font data file, expected '{self.char}' but got '{data[0]}'")
            if len(self.rgbTotals) != 3 or not all(map(lambda x: isinstance(x, int) and 0 <= x <= 255, self.rgbTotals)):
                raise ValueError(f"Invalid rgb totals in font data file for character '{self.char}', expected 3 ints between 0 and 255 but got {self.rgbTotals}")
        pixelSheet = Image.open(f"{folder}/pixels.png")
        self.pixels = pixelSheet.crop((index * self.pixels.width, 0, (index + 1) * self.pixels.width, self.pixels.height))
