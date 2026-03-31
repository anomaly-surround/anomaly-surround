"""App icon - speaker with sound waves."""
import os
from PIL import Image, ImageDraw


def create_icon(size=64):
    """Create a speaker with sound waves icon."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Scale factor
    s = size / 64

    # Background rounded rectangle
    draw.rounded_rectangle(
        [int(2*s), int(2*s), int(62*s), int(62*s)],
        radius=int(14*s), fill="#7c3aed"
    )

    # Speaker body (trapezoid shape using polygon)
    draw.polygon([
        (int(12*s), int(24*s)),  # top-left
        (int(22*s), int(18*s)),  # top-right
        (int(22*s), int(46*s)),  # bottom-right
        (int(12*s), int(40*s)),  # bottom-left
    ], fill="white")

    # Speaker cone (rectangle)
    draw.rectangle(
        [int(8*s), int(26*s), int(14*s), int(38*s)],
        fill="white"
    )

    # Sound waves (arcs)
    wave_color = "#e0d4ff"
    # Wave 1 (closest)
    draw.arc(
        [int(24*s), int(18*s), int(38*s), int(46*s)],
        start=-45, end=45, fill=wave_color, width=max(int(2.5*s), 2)
    )
    # Wave 2 (middle)
    draw.arc(
        [int(30*s), int(13*s), int(46*s), int(51*s)],
        start=-45, end=45, fill=wave_color, width=max(int(2.5*s), 2)
    )
    # Wave 3 (farthest)
    draw.arc(
        [int(36*s), int(8*s), int(54*s), int(56*s)],
        start=-45, end=45, fill=wave_color, width=max(int(2.5*s), 2)
    )

    return img


def create_ico(path):
    """Generate a .ico file with multiple sizes."""
    sizes = [16, 32, 48, 64, 128, 256]
    images = [create_icon(s) for s in sizes]
    images[0].save(path, format="ICO", sizes=[(s, s) for s in sizes],
                   append_images=images[1:])


def get_ico_path():
    """Get path to the .ico file, creating it if needed."""
    ico_path = os.path.join(os.path.dirname(__file__), "app.ico")
    if not os.path.exists(ico_path):
        create_ico(ico_path)
    return ico_path
