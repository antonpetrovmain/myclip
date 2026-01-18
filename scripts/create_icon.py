#!/usr/bin/env python3
"""Create a modern minimal clipboard icon for MyClip."""

from pathlib import Path

from PIL import Image, ImageDraw

# Icon sizes needed for macOS .icns
SIZES = [16, 32, 64, 128, 256, 512, 1024]


def create_clipboard_icon(size: int) -> Image.Image:
    """Create a modern minimal clipboard icon."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Scale factor
    s = size / 100

    # Colors
    board_color = (90, 160, 220)  # Soft blue
    clip_color = (60, 120, 180)  # Darker blue
    paper_color = (255, 255, 255)  # White
    line_color = (200, 200, 200)  # Light gray for text lines

    # Clipboard board (rounded rectangle)
    board_margin = int(12 * s)
    board_top = int(18 * s)
    draw.rounded_rectangle(
        [board_margin, board_top, size - board_margin, size - board_margin],
        radius=int(8 * s),
        fill=board_color,
    )

    # Paper on clipboard
    paper_margin = int(18 * s)
    paper_top = int(28 * s)
    draw.rounded_rectangle(
        [paper_margin, paper_top, size - paper_margin, size - int(18 * s)],
        radius=int(4 * s),
        fill=paper_color,
    )

    # Text lines on paper
    line_height = int(8 * s)
    line_gap = int(12 * s)
    line_start_y = int(38 * s)
    line_margin = int(26 * s)

    for i in range(4):
        y = line_start_y + i * line_gap
        # Vary line lengths
        line_end = size - line_margin - (int(15 * s) if i % 2 else 0)
        if y + line_height < size - int(25 * s):
            draw.rounded_rectangle(
                [line_margin, y, line_end, y + int(4 * s)],
                radius=int(2 * s),
                fill=line_color,
            )

    # Clip at top
    clip_width = int(30 * s)
    clip_height = int(16 * s)
    clip_x = (size - clip_width) // 2
    clip_y = int(10 * s)
    draw.rounded_rectangle(
        [clip_x, clip_y, clip_x + clip_width, clip_y + clip_height],
        radius=int(4 * s),
        fill=clip_color,
    )

    # Clip hole
    hole_width = int(14 * s)
    hole_height = int(6 * s)
    hole_x = (size - hole_width) // 2
    hole_y = int(13 * s)
    draw.rounded_rectangle(
        [hole_x, hole_y, hole_x + hole_width, hole_y + hole_height],
        radius=int(2 * s),
        fill=board_color,
    )

    return img


def main():
    """Generate icon files."""
    output_dir = Path(__file__).parent.parent / "resources"
    output_dir.mkdir(exist_ok=True)

    iconset_dir = output_dir / "MyClip.iconset"
    iconset_dir.mkdir(exist_ok=True)

    # Generate all sizes
    for size in SIZES:
        icon = create_clipboard_icon(size)
        # Standard resolution
        icon.save(iconset_dir / f"icon_{size}x{size}.png")
        # Retina (@2x) - use next size up
        if size <= 512:
            icon_2x = create_clipboard_icon(size * 2)
            icon_2x.save(iconset_dir / f"icon_{size}x{size}@2x.png")

    print(f"Icon set created in {iconset_dir}")
    print("Run: iconutil -c icns resources/MyClip.iconset")


if __name__ == "__main__":
    main()
