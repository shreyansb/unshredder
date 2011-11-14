from PIL import Image
image = Image.open(‘file.jpg’)
data = image.getdata() # This gets pixel data
# Access an arbitrary pixel. Data is stored as a 2d array where rows are
# sequential. Each element in the array is a RGBA tuple (red, green, blue,
# alpha).

x, y = 20, 90
def get_pixel_value(x, y):
    width, height = image.size
    pixel = data[y * width + x]
    return pixel

print get_pixel_value(20, 30)

# Create a new image of the same size as the original
# and copy a region into the new image
NUMBER_OF_COLUMNS = 5
unshredded = Image.new(“RGBA”, image.size)
shred_width = unshredded.size[0]/NUMBER_OF_COLUMNS
shred_number = 1
x1, y1 = shred_width * shred_number, 0
x2, y2 = x1 + shred_width, height
source_region = image.crop(x1, y1, x2, y2)
destination_point = (0, 0)
unshredded.paste(source_region, destination_point)
# Output the new image
unshredded.save(“unshredded.jpg”, “JPEG”)
