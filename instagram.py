"""A solution to http://bit.ly/sCMAD5
by Shreyans Bhansali
written on Sunday, the 13th of November, 2011
"""

from PIL import Image
from itertools import islice, count

class Unshredder():
    pixel_diff_threshold = 25       # consider two pixel attrs a match if their diff 
                                    # is less than this number
    column_match_threshold = 0.75   # consider two columns a match if more than
                                    # this portion of their pixels match

    def __init__(self, image_file='TokyoPanoramaShredded.png', strip_width=32):
        self.image_file = image_file
        self.image = Image.open(image_file)
        self.width, self.height = self.image.size
        self.image_data = list(self.image.getdata())
        self.image_size = len(self.image_data)
        self.strip_width = strip_width
        self.number_of_strips = self.width / strip_width
        # create a list of empty lists, with room for the left and right most
        # pixels for each strip
        self.strip_edges = [[] for i in range(self.number_of_strips*2)]
        self.sort_order = range(self.number_of_strips)
        self.set_strip_edges()

    def unshred(self):
        self.set_strip_edges()
        self.sort_strips()
        self.create_image_from_sort_order()

    def set_strip_edges(self):
        """Collects columns of pixels that represent the left and right
        edges of strips.
        """
        # walk through the image, jumping among strip-edges
        image_iterable = islice(count(), 0, self.image_size+1, self.strip_width)
        # put the pixel and its neighbour into the correct 'column'
        for i, p in enumerate(image_iterable):
            # looking forward to: http://bit.ly/n60KzL
            if p == self.image_size: break
            strip_no = i%(self.number_of_strips)
            l_pixel = self.image_data[p]
            r_pixel = self.image_data[p + self.strip_width - 1]
            self.strip_edges[strip_no*2].append(l_pixel)
            self.strip_edges[(strip_no*2)+1].append(r_pixel)

    def sort_strips(self):
        """Uses self.strip_edges to compare strips and sort them into 
        the original image
        """
    
    def compare_strips(self, s1, s2):
        """Compares two strips and returns if they should be next to each other,
        and if so, in what order
        Returns 1 is s2 is to the right of s1, -1 if s2 is to the left of s1,
        0 if they are not neighbours
        """
        # compare s1 right with s2 left
        s1r = self.strip_edges[(2 * s1) + 1]
        s2l = self.strip_edges[2 * s2]
        diff1 = self.compare_columns(s1r, s2l)
        if diff1:
            return 1

        # compare s1 left with s2 right
        s1l = self.strip_edges[2 * s1]
        s2r = self.strip_edges[(2 * s2) + 1]
        diff2 = self.compare_columns(s1l, s2r)
        if diff2:
            return -1

        return 0

    def compare_columns(self, col1, col2):
        """Compare two columns of pixels.
        Returns 1 is they are deemed neighbours, 0 otherwise.
        """
        total_matches = 0.0
        for i in xrange(self.height):
            total_matches += self.compare_pixels(col1[i], col2[i])
        print total_matches, self.height, round((total_matches / self.height),2)
        if (total_matches / self.height) > self.column_match_threshold:
            return 1
        return 0

    def compare_pixels(self, p1, p2):
        """Compare two pixels.
        Returns 1 if they are deemed neighbours, 0 otherwise
        """
        print p1, p2
        for i in range(4):
            if abs(p1[i] - p2[i]) > self.pixel_diff_threshold:
                return 0
        return 1

    def create_image_from_sort_order(self):
        """Creates a new image based on the order of strips in self.sort_order
        """
        unshredded = Image.new("RGBA", self.image.size)
        for i, strip_no in enumerate(self.sort_order):
            strip = self.get_strip(strip_no)
            destination_point_top_left = (i * self.strip_width, 0)
            unshredded.paste(strip, destination_point_top_left)
            unshredded.save("unshredded.png", "PNG")

    def get_strip(self, strip_no):
        """Returns an ImageCrop object for the strip
        """
        x1, y1 = self.strip_width * strip_no, 0
        x2, y2 = x1 + self.strip_width, self.height
        return self.image.crop((x1, y1, x2, y2))
