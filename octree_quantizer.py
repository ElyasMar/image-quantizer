from color import Color


class OctreeNode(object):
    """
    Octree Node class for color quantization
    """

    def __init__(self, level, parent):
        """
        Init new Octree Node with optimizations
        """
        self.color = Color(0, 0, 0)
        self.pixel_count = 0
        self.palette_index = 0
        self.children = [None for _ in range(8)]
        # add node to current level for faster reduction
        if level < OctreeQuantizer.MAX_DEPTH - 1:
            parent.add_level_node(level, self)

    def is_leaf(self):
        """
        Check that node is leaf (has pixel data)
        """
        return self.pixel_count > 0

    def get_leaf_nodes(self):
        """
        Get all leaf nodes efficiently
        """
        leaf_nodes = []
        for node in self.children:
            if node:
                if node.is_leaf():
                    leaf_nodes.append(node)
                else:
                    leaf_nodes.extend(node.get_leaf_nodes())
        return leaf_nodes

    def get_nodes_pixel_count(self):
        """
        Get a sum of pixel count for node and its children
        """
        sum_count = self.pixel_count
        for node in self.children:
            if node:
                sum_count += node.pixel_count
        return sum_count

    def add_color(self, color, level, parent):
        """
        Add color to the tree with bounds checking
        """
        if level >= OctreeQuantizer.MAX_DEPTH:
            self.color.red += color.red
            self.color.green += color.green
            self.color.blue += color.blue
            self.pixel_count += 1
            return

        index = self.get_color_index_for_level(color, level)
        if not self.children[index]:
            self.children[index] = OctreeNode(level, parent)
        self.children[index].add_color(color, level + 1, parent)

    def get_palette_index(self, color, level):
        """
        Get palette index for color with fallback
        """
        if self.is_leaf():
            return self.palette_index

        index = self.get_color_index_for_level(color, level)
        if self.children[index]:
            return self.children[index].get_palette_index(color, level + 1)
        else:
            # get palette index for first available child node
            for node in self.children:
                if node:
                    return node.get_palette_index(color, level + 1)
            # fallback to current node if no children
            return self.palette_index

    def remove_leaves(self):
        """
        Add all children pixels count and color channels to parent node
        Return the number of removed leaves for counting
        """
        result = 0
        for node in self.children:
            if node:
                self.color.red += node.color.red
                self.color.green += node.color.green
                self.color.blue += node.color.blue
                self.pixel_count += node.pixel_count
                result += 1
        return result - 1 if result > 0 else 0

    def get_color_index_for_level(self, color, level):
        """
        Get index of color for next level using bit manipulation
        """
        index = 0
        mask = 0x80 >> level
        if color.red & mask:
            index |= 4
        if color.green & mask:
            index |= 2
        if color.blue & mask:
            index |= 1
        return index

    def get_color(self):
        """
        Get average color with division by zero protection
        """
        if self.pixel_count == 0:
            return Color(0, 0, 0)

        return Color(
            int(self.color.red / self.pixel_count),
            int(self.color.green / self.pixel_count),
            int(self.color.blue / self.pixel_count))


class OctreeQuantizer(object):
    """
    Octree Quantizer class for image color quantization
    """

    MAX_DEPTH = 8

    def __init__(self):
        """
        Init Octree Quantizer with optimized data structures
        """
        self.levels = {i: [] for i in range(self.MAX_DEPTH)}
        self.root = OctreeNode(0, self)

    def get_leaves(self):
        """
        Get all leaves efficiently
        """
        return self.root.get_leaf_nodes()

    def add_level_node(self, level, node):
        """
        Add node to the nodes at level for reduction tracking
        """
        self.levels[level].append(node)

    def add_color(self, color):
        """
        Add color to the Octree
        """
        self.root.add_color(color, 0, self)

    def make_palette(self, color_count):
        """
        Make color palette with color_count colors
        with reduction strategy
        """
        palette = []
        palette_index = 0
        leaf_count = len(self.get_leaves())

        # reduce nodes from deepest level first for better quality
        for level in range(self.MAX_DEPTH - 1, -1, -1):
            if self.levels[level] and leaf_count > color_count:
                nodes_to_process = self.levels[level][:]  # copy list
                for node in nodes_to_process:
                    if leaf_count <= color_count:
                        break
                    leaves_removed = node.remove_leaves()
                    leaf_count -= leaves_removed
                # clear processed level
                self.levels[level] = []

            if leaf_count <= color_count:
                break

        # build palette from remaining leaves
        leaves = self.get_leaves()
        for node in leaves:
            if palette_index >= color_count:
                break
            if node.is_leaf():
                palette.append(node.get_color())
                node.palette_index = palette_index
                palette_index += 1

        return palette

    def get_palette_index(self, color):
        """
        Get palette index for color
        """
        return self.root.get_palette_index(color, 0)

    def get_stats(self):
        """
        Get quantizer statistics while debugging
        """
        total_nodes = 0
        for level_nodes in self.levels.values():
            total_nodes += len(level_nodes)

        return {
            'total_nodes': total_nodes,
            'leaf_count': len(self.get_leaves()),
            'levels': {level: len(nodes) for level, nodes in self.levels.items() if nodes}
        }