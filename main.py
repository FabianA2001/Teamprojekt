from PIL import Image, ImageDraw, ImageFont


class Img:
    def __init__(self) -> None:
        self.img = Image.new("RGB", (1700, 1700), color="white")
        self._draw = ImageDraw.Draw(self.img)
        width, height = 200, 200
        line_color = "black"
        line_width = 5
        self._draw.line((width // 2, 0, width // 2, height),
                        fill=line_color, width=line_width)
        # Horizontal line
        self._draw.line((0, height // 2, width, height // 2),
                        fill=line_color, width=line_width)

    def gernerte_point(self, height, withe, count) -> list[tuple[int, int]]:
        return [(1, 2), (2, 3)]


if __name__ == "__main__":
    img = Img()
    img.img.save("Test.jpg")
