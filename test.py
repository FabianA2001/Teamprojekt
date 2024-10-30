from PIL import Image, ImageDraw

# Define image size and background color
original_width = 800
original_height = 800
background_color = (255, 255, 255)  # White background

# Create a new blank image at a larger size
image = Image.new("RGB", (original_width, original_height), background_color)
draw = ImageDraw.Draw(image)

# Define coordinates (x1, y1) and (x2, y2)
coordinates = [
    (100, 100),
    (600, 200),
    (300, 500),
    (700, 700),
    (100, 700)
]

# Draw lines connecting the coordinates
for i in range(len(coordinates) - 1):
    draw.line([coordinates[i], coordinates[i + 1]],
              fill=(0, 128, 255), width=10)

# Optionally, draw points at the coordinates
for coord in coordinates:
    draw.ellipse([coord[0] - 10, coord[1] - 10, coord[0] +
                 10, coord[1] + 10], fill=(255, 0, 0))

# Resize the image to create a smooth appearance using LANCZOS
image = image.resize((400, 400), Image.LANCZOS)

# Save the image
image.save("anti_aliased_coordinates_lines.jpg")
print("Image saved as anti_aliased_coordinates_lines.jpg")
