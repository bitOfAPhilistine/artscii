import os, sys, math
from PIL import Image, ImageDraw, ImageFont, ImageText


class Char:
    def __init__(self, char: str, font: ImageFont.ImageFont, fontSize: int, index: int | None = None):
        self.char = char
        self.rgbTotals = (0, 0, 0)
        cellSize = (round(fontSize * 0.6), round(fontSize * 1.2))
        self.pixels = Image.new("RGB", cellSize) # r is horizontal bias, g is vertical bias, b is overall brightness
        self.rawPixels = Image.new("1", cellSize) # Used for generating the rgb values, saved for debugging

        # Load the character's pixel data from the font file, if index is provided, otherwise generate it
        if index is not None:
            self.load_from_files(index, f"fonts/{font.getname()[0]}-{font.getname()[1]}-{fontSize}")
        else:
            ImageDraw.Draw(self.rawPixels).text((0, 0), char, font=font, fill=255)
            self.init_from_raw(self.rawPixels)
            self.apply_expansion_filter()

    def to_string(self):
        # Return a string with the character, and its rgb totals
        return f"{self.char}{self.rgbTotals[0]},{self.rgbTotals[1]},{self.rgbTotals[2]}"
    
    def init_from_raw(self, rawPixels: Image.Image):
        for x in range(rawPixels.width):
            for y in range(rawPixels.height):
                pixel = rawPixels.getpixel((x, y))
                if pixel > 0:
                    toCheck = ((x + 1, y), (x, y + 1), (x - 1, y), (x, y - 1))
                    rgb = (0, 0, 255)
                    for i in range(2):
                        check1 = toCheck[i]
                        check2 = toCheck[i + 2]
                        checkPix1 = 0
                        checkPix2 = 0
                        try:
                            checkPix1 = rawPixels.getpixel(check1)
                        except:
                            pass
                        try:
                            checkPix2 = rawPixels.getpixel(check2)
                        except:
                            pass

                        if checkPix1 > 0 and checkPix2 > 0:
                            if i == 0:
                                rgb = (rgb[0] + 255, rgb[1], 255)
                            elif i == 1:
                                rgb = (rgb[0], rgb[1] + 255, 255)
                    self.pixels.putpixel((x, y), rgb)
                    self.rgbTotals = (self.rgbTotals[0] + rgb[0], self.rgbTotals[1] + rgb[1], self.rgbTotals[2] + rgb[2])
    
    def apply_expansion_filter(self):
        # Apply an expansion filter to the pixels, spreading brighter pixels to nearby darker pixels, with r only spreading horizontally, and g only spreading vertically
        newPixels = self.pixels.copy()
        biasExpDist = self.pixels.width / 2
        brightExpDist = self.pixels.width / 4

        toCheck = []
        for i in range(1, math.floor(biasExpDist) + 1):
            # Add pixels in a cross shape out to biasExpDist and a diamond shape out to brightExpDist, third value is the colors to be affected
            if i <= brightExpDist:
                toCheck.append((i, 0, 'rb'))
                toCheck.append((-i, 0, 'rb'))
                toCheck.append((0, i, 'gb'))
                toCheck.append((0, -i, 'gb'))

                for j in range(1, i):
                    toCheck.append((i - j, j, 'b'))
                    toCheck.append((-i + j, -j, 'b'))
                    toCheck.append((-j, i - j, 'b'))
                    toCheck.append((j, -i + j, 'b'))
            else:
                toCheck.append((i, 0, 'r'))
                toCheck.append((-i, 0, 'r'))
                toCheck.append((0, i, 'g'))
                toCheck.append((0, -i, 'g'))
        
        for x in range(self.pixels.width):
            for y in range(self.pixels.height):
                pixel = self.pixels.getpixel((x, y))
                # B is overall brightness so only it needs to be checked
                if pixel[2] > 0:
                    for c in toCheck:
                        currentDist = math.sqrt(c[0] ** 2 + c[1] ** 2)
                        check = (x + c[0], y + c[1])
                        
                        if check[0] < 0 or check[0] >= self.pixels.width or check[1] < 0 or check[1] >= self.pixels.height:
                            continue
                        newPix = newPixels.getpixel(check)
                        
                        if 'r' in c[2]:
                            val = round(pixel[0] * (biasExpDist - currentDist) / biasExpDist)
                            newPix = (max(val, newPix[0]), newPix[1], newPix[2])
                        elif 'g' in c[2]:
                            val = round(pixel[1] * (biasExpDist - currentDist) / biasExpDist)
                            newPix = (newPix[0], max(val, newPix[1]), newPix[2])
                        
                        if 'b' in c[2]:
                            val = round(pixel[2] * (brightExpDist - currentDist) / brightExpDist)
                            newPix = (newPix[0], newPix[1], max(val, newPix[2]))
                        
                        newPixels.putpixel(check, newPix)
        
        self.pixels = newPixels

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
