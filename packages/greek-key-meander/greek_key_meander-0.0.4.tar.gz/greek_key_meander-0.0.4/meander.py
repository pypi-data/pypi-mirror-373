import drawsvg as draw
import cairosvg
import argparse

class GreekKeyConfig:
    def __init__(self, key_unit_length, width_units, height_units):
        # The size of greek key unit
        self.key_unit_length = key_unit_length
        # Number of greek key units horizontally
        self.width_units = width_units
        # Number of greek key units vertically
        self.height_units = height_units
        self.key_pattern_length = self.key_unit_length * 5

    def get_canvas_size(self):
        width = self.width_units * self.key_pattern_length + 3 * self.key_unit_length
        height = self.height_units * self.key_pattern_length + 3 * self.key_unit_length
        return width, height

    def get_start_position(self):
        start_x = 1.5 * self.key_unit_length
        start_y = 6.5 * self.key_unit_length
        return start_x, start_y

    def get_outer_frame_size(self):
        outer_x = 0.5 * self.key_unit_length
        outer_y = 0.5 * self.key_unit_length
        outer_width = self.width_units * self.key_pattern_length + 2 * self.key_unit_length
        outer_height = self.height_units * self.key_pattern_length + 2 * self.key_unit_length
        return outer_x, outer_y, outer_width, outer_height

    def get_inner_frame_size(self):
        inner_x = 6.5 * self.key_unit_length
        inner_y = 6.5 * self.key_unit_length
        inner_width = (self.width_units - 2) * self.key_pattern_length
        inner_height = (self.height_units - 2) * self.key_pattern_length
        return inner_x, inner_y, inner_width, inner_height


def draw_horizontal_unit(path):
    """Draws a single horizontal unit of the meander pattern."""
    key_unit_length = config.key_unit_length
    path.v(-4 * key_unit_length)
    path.h(4 * key_unit_length)
    path.v(3 * key_unit_length)
    path.h(-2 * key_unit_length)
    path.v(-key_unit_length)
    path.h(key_unit_length)
    path.v(-key_unit_length)
    path.h(-2 * key_unit_length)
    path.v(3 * key_unit_length)
    path.h(4 * key_unit_length)


def draw_vertical_unit(path):
    """Draws a single vertical unit of the meander pattern."""
    key_unit_length = config.key_unit_length
    path.h(4 * key_unit_length)
    path.v(4 * key_unit_length)
    path.h(-3 * key_unit_length)
    path.v(-2 * key_unit_length)
    path.h(key_unit_length)
    path.v(key_unit_length)
    path.h(key_unit_length)
    path.v(-2 * key_unit_length)
    path.h(-3 * key_unit_length)
    path.v(4 * key_unit_length)

def draw_horizontal_unit_right_to_left(path):
    """Draws a single horizontal unit of the meander pattern, from right to left."""
    key_unit_length = config.key_unit_length
    path.h(-4*key_unit_length)
    path.v(-3*key_unit_length)
    path.h(2*key_unit_length)
    path.v(1*key_unit_length)
    path.h(-key_unit_length)
    path.v(1*key_unit_length)
    path.h(2*key_unit_length)
    path.v(-3*key_unit_length)
    path.h(-4*key_unit_length)
    path.v(4*key_unit_length)

def draw_vertical_unit_bottom_up(path):
    """Draws a single vertical unit of the meander pattern, bottom up."""
    key_unit_length = config.key_unit_length
    path.v(-4*key_unit_length)
    path.h(3*key_unit_length)
    path.v(2*key_unit_length)
    path.h(-key_unit_length)
    path.v(-key_unit_length)
    path.h(-key_unit_length)
    path.v(2*key_unit_length)
    path.h(3*key_unit_length)
    path.v(-4*key_unit_length)
    path.h(-4*key_unit_length)


def draw_frame(path, x, y, w, h):
    """Draws a rectangular frame using a path."""
    path.M(x, y)
    path.h(w)
    path.v(h)
    path.h(-w)
    path.v(-h)
    path.Z()


def draw_greek_key_unit(path):
    """Draws the main meander pattern."""
    start_x, start_y = config.get_start_position()
    key_unit_length = config.key_unit_length
    key_pattern_length = config.key_pattern_length
    width_units = config.width_units
    height_units = config.height_units

    # top line
    path.M(start_x, start_y)
    path.v(-key_unit_length)
    for _ in range(width_units - 1):
        draw_horizontal_unit(path)
    path.v(-4 * key_unit_length)
    path.h(key_unit_length)
    # right line
    for _ in range(height_units - 1):
        draw_vertical_unit(path)

    path.h(4*key_unit_length)
    path.v(5*key_unit_length)

    # bottom line
    for _ in range(width_units -1):
        draw_horizontal_unit_right_to_left(path)

    path.h(-5*key_unit_length)

    # left line
    for _ in range(height_units - 1):
        draw_vertical_unit_bottom_up(path)

    path.Z()

def generate_pattern_svg(stroke_width=2, stroke_color='black', stroke_opacity=1.0, filename='meander'):
    """Generates the complete SVG drawing."""
    width, height = config.get_canvas_size()
    d = draw.Drawing(width, height, origin=(0, 0), displayInline=False)
    path = draw.Path(
        stroke=stroke_color,
        stroke_width=stroke_width,
        stroke_opacity=stroke_opacity,
        fill='none',
        #stroke_linecap='square'
    )

    draw_greek_key_unit(path)

    # Draw frames
    draw_frame(path, *config.get_outer_frame_size())
    draw_frame(path, *config.get_inner_frame_size())

    d.append(path)
    d.save_svg(f'{filename}.svg')

    cairosvg.svg2png(url=f'{filename}.svg', write_to=f'{filename}.png', output_width=width, output_height=height)


def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Draw a Greek key pattern SVG and PNG with customizable line properties.")
    parser.add_argument('--stroke-width', type=float, default=6.0, help="Line thickness in pixels (default: 2.0)")
    parser.add_argument('--stroke-color', type=str, default='#AB8E0E', help="Line color: name (e.g., 'red'), hex (e.g., '#FF0000'), or RGB (e.g., '255,0,0') (default: '#AB8E0E')")
    parser.add_argument('--stroke-opacity', type=float, default=0.7, help="Line transparency, 0.0 (transparent) to 1.0 (opaque) (default: 0.7)")
    parser.add_argument('--size', type=int, default=25, help="This defines the size of the pattern (default: 25)")
    parser.add_argument('--width', type=int, default=16, help="The number of patterns horizontally (default: 16)")
    parser.add_argument('--height', type=int, default=9, help="The number of patterns vertically (default: 9)")
    parser.add_argument('--file', type=str, default='meander', help="File name for svg and png (default: `meander`)")

    # Parse arguments
    args = parser.parse_args()

    global config

    config = GreekKeyConfig(args.size, args.width, args.height)

    generate_pattern_svg(
        stroke_width=args.stroke_width,              # Thicker line (2 pixels)
        stroke_color=args.stroke_color,              # Gold color (hex)
        stroke_opacity=args.stroke_opacity,           # 70% opacity
        filename=args.file
    )

if __name__ == '__main__':
    main()
