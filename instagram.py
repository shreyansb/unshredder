"""A solution to http://bit.ly/sCMAD5
by Shreyans Bhansali
written on Sunday, the 13th of November, 2011
"""
from PIL import Image

class Unshredder():
    pixel_diff_threshold = 15       # consider two pixel attrs a match if their diff 
                                    # is less than this number
    column_match_threshold = 0.30   # consider two columns a match if more than
                                    # this portion of their pixels match
    column_match_step = 0.03        # if we don't find a match, we lower the threshold
                                    # by this much

    def __init__(self, image_file='TokyoPanoramaShredded.png'):
        print "initializing %s..." % image_file
        self.image_file = image_file
        self.image = Image.open(image_file)
        self.width, self.height = self.image.size
        self.image_data = list(self.image.getdata())
        self.image_size = len(self.image_data)
        self.strip_width = self.detect_strip_width()     ### Bonus!
        self.number_of_strips = self.width / self.strip_width
        # list to hold the edges of each strip
        self.strip_edges = [[] for i in range(self.number_of_strips*2)]
        self.sort_order = [self.number_of_strips-1]
        image_file_parts = image_file.rsplit('.')
        self.output_filename = '%s-unshredded.%s' % (image_file_parts[0], image_file_parts[1])
        self.unshredded = None
        self.unshred()

    def unshred(self):
        self.set_strip_edges()
        print "unshredding..."
        self.sort_strips()
        self.create_image_from_sort_order()
        self.image.show()
        self.unshredded.show()

    def set_strip_edges(self):
        """Collects columns of pixels that represent the left and right
        edges of strips.
        """
        # walk through the image, jumping among strip-edges
        image_iterable = xrange(0, self.image_size+1, self.strip_width)
        # put the pixel and its neighbour into the correct 'column'
        for i, p in enumerate(image_iterable):
            # looking forward to: http://bit.ly/n60KzL
            if p == self.image_size: 
                break
            strip_no = i%(self.number_of_strips)
            l_pixel = self.image_data[p]
            self.strip_edges[strip_no*2].append(l_pixel)
            r_pixel = self.image_data[p + self.strip_width - 1]
            self.strip_edges[(strip_no*2)+1].append(r_pixel)

    def sort_strips(self):
        """Uses self.strip_edges to compare strips and sort them into 
        the original image
        If we don't find a match, we reduce accuracy until we do
        """
        starting_order = list(self.sort_order)
        self.get_neighbours()
        if len(self.sort_order) < self.number_of_strips:
            if starting_order == self.sort_order:
                self.column_match_threshold -= self.column_match_step
            self.sort_strips()
        else:
            print "done."
            return

    def get_neighbours(self):
        """Finds strips to go on the left of, and right of the 
        leftmost and right most strips
        """
        l_most_strip = self.sort_order[0]
        r_most_strip = self.sort_order[-1]
        left, right = None, None
        for i in range(self.number_of_strips):
            if i in self.sort_order: continue
            left = self.compare_strips(i, l_most_strip)
            if left != None:
                self.sort_order = [i] + self.sort_order
                break
        for i in range(self.number_of_strips):
            if i in self.sort_order: continue
            right = self.compare_strips(r_most_strip, i)
            if right != None:
                self.sort_order = self.sort_order + [i]
                break
    
    def compare_strips(self, s1, s2):
        """Compares two strips and returns 1 if s2 should be to
        the right of s1
        """
        s1r = self.strip_edges[(2 * s1) + 1]
        s2l = self.strip_edges[2 * s2]
        if self.compare_columns(s1r, s2l):
            return 1
        return None

    def compare_columns(self, col1, col2):
        """Compare two columns of pixels.
        Returns 1 is they are deemed neighbours, 0 otherwise.
        """
        total_matches = 0.0
        for i in xrange(self.height):
            total_matches += self.compare_pixels(col1[i], col2[i])
        if (total_matches / self.height) > self.column_match_threshold:
            return 1
        return 0

    def compare_pixels(self, p1, p2):
        """Compare two pixels.
        Returns 1 if they are deemed neighbours, 0 otherwise
        """
        for i in range(3):
            if abs(p1[i] - p2[i]) > self.pixel_diff_threshold:
                return 0
        return 1

    def create_image_from_sort_order(self):
        """Creates a new image based on the order of strips in self.sort_order
        """
        self.unshredded = Image.new("RGBA", self.image.size)
        for i, strip_no in enumerate(self.sort_order):
            strip = self.get_strip(strip_no)
            destination_point_top_left = (i * self.strip_width, 0)
            self.unshredded.paste(strip, destination_point_top_left)
        self.unshredded.save(self.output_filename, "PNG")
        print "saved the unshredded file as %s" % self.output_filename

    def get_strip(self, strip_no):
        """Returns an ImageCrop object for the strip
        """
        x1, y1 = self.strip_width * strip_no, 0
        x2, y2 = x1 + self.strip_width, self.height
        return self.image.crop((x1, y1, x2, y2))

    def detect_strip_width(self):
        """Returns the width of the strips, assuming constant width
        """
        for i in range(self.width):
            col1 = self.get_column_of_pixels(i)
            col2 = self.get_column_of_pixels(i+1)
            if not self.compare_columns(col1, col2):
                print "detected strip width of %s pixels..." % str(i+1)
                return i+1
    
    def get_column_of_pixels(self, x_coord):
        """Returns the column of pixels for the given x coordinate
        """
        pixels = list()
        for y in range(self.height):
            pixels.append(self.image_data[y * self.width + x_coord])
        return pixels
