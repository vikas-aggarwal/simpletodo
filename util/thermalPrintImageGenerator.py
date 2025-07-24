from PIL import Image, ImageDraw, ImageFont
import re
import io

def create_image_from_list(title, items, width_in_inches=2, dpi=300, font_path="DejaVuSans.ttf", font_size=50, output_file="output.png"):
    # Set dimensions
    width_px = int(width_in_inches * dpi)
    #bullet_char="☐"
    bullet_char = "•"
    font = ImageFont.truetype(font_path, font_size)

    # Prepare drawing context to calculate size
    dummy_img = Image.new("RGB", (width_px, 1000), color="white")
    draw = ImageDraw.Draw(dummy_img)

    # Wrap and calculate height
    wrapped_lines = []
    boundary = draw.textbbox((0, 0), "A", font=font)
    line_height = boundary[3]  - boundary[1] + 20
    total_height=0

    for item in items:
        boundary = draw.textbbox((0, 0), bullet_char+" "+item, font=font)
        if(boundary[2] - boundary[0]) > width_px:
            words = re.split(r"(\s+)", bullet_char+" "+item)
            #find the max items that can be accomodated
            currPosition=0
     
            while currPosition < len(words):
                currentIndex = currPosition
                while currentIndex < len(words):
                    currBoundary = draw.textbbox((0, 0), "".join(words[currPosition:currentIndex+1]), font=font)
                    if (currBoundary[2] - currBoundary[0]) > width_px:
                        wrapped_lines.append("".join(words[currPosition:currentIndex]))
                        currPosition = currentIndex
                        break
                    currentIndex+=1
                if currentIndex >= len(words):
                    wrapped_lines.append("".join(words[currPosition:currentIndex]))
                    break        
        else:
            wrapped_lines.append( bullet_char+" "+item)

    total_height = line_height * len(wrapped_lines) + (line_height * 3)+ 20


    # Create image with calculated height
    img = Image.new("RGB", (width_px, total_height), color="white")
    draw = ImageDraw.Draw(img)

    # Print title

    draw.text((width_px/2,10), title, font=font, fill="black", anchor="mt")

    # Draw text
    y = line_height + 10
    for line in wrapped_lines:
        draw.text((0, y), line, font=font, fill="black")
        y += line_height

    # Save image
    imageBytes = io.BytesIO()
    img.save(imageBytes, format="PNG")
    imageBytes.seek(0)
    return imageBytes

# Example usage
#items = [
#    "Hello",
#    "This is a short line.",
#    "This line is much longer and should automatically wrap to fit within the 2-inch width.",
#    "Another brief one.",
#    "A final item that might be long enough to require wrapping again, depending on the font size."
#]
#
#create_image_from_list(items)
#