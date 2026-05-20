import os, sys
from PIL import Image, ImageDraw, ImageFont, ImageText

# Get image name from user and confirm it exists in the Images folder
print("Enter the name of the image you want to convert to ASCII art (must be in the Images folder):")
imagePath = f"images/{input('')}"
while not os.path.exists(imagePath):
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

ascii = '''☺☻♥♦♣♠•◘○◙♂♀♪♫☼►◄↕‼¶§▬↨↑↓→←∟↔▲▼ 
!"#$%&'()*+,-./0123456789:;<=>?@
ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`
abcdefghijklmnopqrstuvwxyz{|}~∙·
ÇüéâäàåçêëèïîìÄÅÉæÆôöòûùÿÖÜø£Ø₧ƒ
áíóúñÑªº¿®¬½¼¡«»░▒▓│┤ÁÂÀ©╣║╗╝¢¥┐
└┴┬├─┼ãÃ╚╔╩╦╠═╬¤ðÐÊËÈıÍÎÏ┘┌█▄▌▐▀
αßΓπΣσµτΦΘΩδ∞φε∩≡±≥≤⌠⌡÷≈°√ⁿ²■'''

# Get the terminal font
font = ImageFont.truetype("fonts/UbuntuMono.ttf", fontSize)

# Check for a font sheet image jpg in the fonts folder and create one if it doesn't exist
fontSheetPath = f"fonts/fontsheet_{font.getname()[0]}_{font.getname()[1]}_{fontSize}.jpg"
if not os.path.exists(fontSheetPath):
    fontSheetText = ImageText.Text(ascii, font)

    # Create a new image to draw the font sheet on
    fontSheet = Image.new("RGB", (fontSize * 16, fontSize * 16))
    draw = ImageDraw.Draw(fontSheet)
    
    # Draw each character in the ascii string onto the font sheet
    for i, char in enumerate(ascii):
        x = (i % 16) * fontSize
        y = (i // 16) * fontSize
        draw.text((x, y), char, font=font, fill="white")
    
    # Save the font sheet image
    fontSheet.save(fontSheetPath)


def main():
    pass

if __name__ == "__main__":
    main()