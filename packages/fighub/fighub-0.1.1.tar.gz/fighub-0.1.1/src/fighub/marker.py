def marker_schedule(marker_schedule=None):
    if marker_schedule == "SPBM":
        based_marker = {
            "ADAM": "s",  # square
            "ALR-SMAG": "h",  # pixel marker
            "Bundle": "o",  # circle
            "SGD": "p",  # pentagon
            "SPSmax": "4",  # tri-right
            "SPBM-PF": "*",  # star
            "SPBM-TR": "^",  # star
        }
    else:

        based_marker = {
            "point": ".",  # point marker
            "pixel": ",",  # pixel marker
            "circle": "o",  # circle
            "triangle_down": "v",  # down triangle
            "triangle_up": "^",  # up triangle
            "triangle_left": "<",  # left triangle
            "triangle_right": ">",  # right triangle
            "tri_down": "1",  # tri-down
            "tri_up": "2",  # tri-up
            "tri_left": "3",  # tri-left
            "tri_right": "4",  # tri-right
            "square": "s",  # square
            "pentagon": "p",  # pentagon
            "star": "*",  # star
            "hexagon1": "h",  # hexagon 1
            "hexagon2": "H",  # hexagon 2
            "plus": "+",  # plus
            "x": "x",  # x
            "diamond": "D",  # diamond
            "thin_diamond": "d",  # thin diamond
            "vline": "|",  # vertical line
            "hline": "_",  # horizontal line
        }


    return based_marker