class Color(object):
    """
    Color class
    """

    def __init__(self, red=0, green=0, blue=0):
        """
        Initialize color with validation
        """
        self.red = max(0, min(255, int(red)))
        self.green = max(0, min(255, int(green)))
        self.blue = max(0, min(255, int(blue)))
