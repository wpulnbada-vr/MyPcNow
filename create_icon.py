"""Generate a simple app icon for mypcnow."""

from PIL import Image, ImageDraw, ImageFont
import os

def create_icon():
    """Create a simple shield icon for mypcnow."""
    size = 256
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Shield shape (rounded rectangle as base)
    padding = 20
    shield_color = (37, 99, 235)  # Blue #2563EB

    # Draw shield body
    draw.rounded_rectangle(
        [padding, padding, size - padding, size - padding * 2],
        radius=30,
        fill=shield_color,
    )

    # Draw shield bottom point
    points = [
        (padding, size - padding * 3),
        (size // 2, size - padding),
        (size - padding, size - padding * 3),
    ]
    draw.polygon(points, fill=shield_color)

    # Draw lock icon in center (white)
    cx, cy = size // 2, size // 2 - 10
    lock_color = (255, 255, 255)

    # Lock body
    draw.rounded_rectangle(
        [cx - 35, cy - 5, cx + 35, cy + 45],
        radius=8,
        fill=lock_color,
    )

    # Lock shackle (arc)
    draw.arc(
        [cx - 25, cy - 40, cx + 25, cy + 5],
        start=180,
        end=0,
        fill=lock_color,
        width=8,
    )

    # Keyhole
    draw.ellipse(
        [cx - 8, cy + 10, cx + 8, cy + 26],
        fill=shield_color,
    )
    draw.polygon(
        [(cx - 4, cy + 22), (cx + 4, cy + 22), (cx + 2, cy + 35), (cx - 2, cy + 35)],
        fill=shield_color,
    )

    # Save as ICO
    os.makedirs("assets", exist_ok=True)
    icon_path = os.path.join("assets", "icon.ico")

    # Save multiple sizes for ICO
    sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    icons = [img.resize(s, Image.LANCZOS) for s in sizes]
    icons[0].save(icon_path, format="ICO", sizes=[(s[0], s[1]) for s in sizes], append_images=icons[1:])

    print(f"Icon created: {icon_path}")
    return icon_path


if __name__ == "__main__":
    create_icon()
