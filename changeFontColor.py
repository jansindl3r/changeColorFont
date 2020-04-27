import re
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables.C_P_A_L_ import Color
from fontTools.ttLib.tables import C_P_A_L_, S_V_G_
from typing import Tuple, Union


class ChangeFontColor:
    """
    Tool that changes color in SVG/COLR font. 
    It tries to simplify the process a bit.
    """
    def __init__(self, path: Path, colors, inputType: str) -> None:
        self.font = TTFont(path)
        self.hexColors = (
            colors if inputType == "hex" else list(map(self.rgbToHex, colors))
        )
        self.rgbColors = (
            colors if inputType == "rgb" else list(map(self.hexToRgb, colors))
        )
        svg = self.font.get("SVG ")
        cpal = self.font.get("CPAL")
        if svg:
            self.changeSVGColor(svg)
        if cpal:
            self.changeCPALColor(cpal)
        self.font.save(path.absolute().with_name(f"colored_{path.name}"))

    def changeSVGColor(self, table: S_V_G_) -> None:
        """
        Regexes colors in svg data in given font and changes their color.
        """
        colors = self.hexColors[::-1]
        for i, entry in enumerate(table.docList):
            matches = re.finditer('fill="#([0-9]*)"', entry[0])
            spans = [match.span(1) for match in matches][::-1]
            if i == 0:
                assert len(spans) == len(
                    colors
                ), "have same number of new colors as in your input file"
            for color, (start, end) in zip(colors, spans):
                entry[0] = f"{entry[0][:start]}{color}{entry[0][end:]}"

    def changeCPALColor(self, table: C_P_A_L_) -> None:
        """
        Changes CPAL table in given font, this table contains palettes of colors.
        Currently, it works only with fonts that have only one color in their palette. 
        """
        colors = self.rgbColors

        for i, color in enumerate(colors):
            if len(color) == 3:
                colors[i] += (255,)

        table.palettes = [list(map(lambda x: Color(*x[:3][::-1], x[3]), colors))]

    def hexToRgb(self, val: str) -> Tuple[int, ...]:
        """
        Converts hex value to rgb
        """
        splits = tuple(val[i : i + 2] for i in range(0, len(val), 2))
        rgbSpace = tuple(map(lambda x: int(x, 16), splits))
        return rgbSpace

    def rgbToHex(self, val: Tuple[int, ...]) -> str:
        """
        Converts rgb value to hex
        """
        return "".join(tuple(format(i, "x").zfill(2) for i in val))


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="change colors in color font")
    parser.add_argument("path", type=Path, help="a font file to change color")
    parser.add_argument(
        "colors",
        type=str,
        nargs="+",
        help="new colors, must be same quantity as original colors. Can be hex or rgb/a",
    )
    args = parser.parse_args()

    colorType = "hex"
    for i, color in enumerate(args.colors):
        if "," in color:
            colors = color.split(",")
            colors = list(map(int, colors))
            args.colors[i] = colors
            colorType = "rgb"

    changeFontColor = ChangeFontColor(args.path, args.colors, colorType)
