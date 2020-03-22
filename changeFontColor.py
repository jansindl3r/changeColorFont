import re
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables.C_P_A_L_ import Color


class ChangeFontColor:
    def __init__(self, path, colors, inputType):
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
        self.font.save(path.absolute().with_name(f'colored_{path.name}'))

    def changeSVGColor(self, table):
        colors = self.hexColors[::-1]
        for i, entry in enumerate(table.docList):
            matches = re.finditer('fill="#([0-9]*)"', entry[0])
            spans = [match.span(1) for match in matches][::-1]
            if i == 0:
                assert len(spans) == len(colors),\
                    "have same number of new colors as in your input file"
            for color, (start, end) in zip(colors, spans):
                entry[0] = f"{entry[0][:start]}{color}{entry[0][end:]}"

    def changeCPALColor(self, table):
        colors = self.rgbColors

        for i, color in enumerate(colors):
            if len(color) == 3:
                colors[i] += (255, )

        table.palettes = [list(map(lambda x:Color(*x[:3][::-1], x[3]), colors))]

    def hexToRgb(self, val):
        splits = tuple(val[i : i + 2] for i in range(0, len(val), 2))
        rgbSpace = tuple(map(lambda x: int(x, 16), splits))
        return rgbSpace

    def rgbToHex(self, val):
        return "".join(tuple(format(i, "x").zfill(2) for i in val))

if __name__ == "__main__":
    import argparse


    parser = argparse.ArgumentParser(description="change colors in color font")
    parser.add_argument("path", type=Path, help=".font file to change color")
    parser.add_argument('colors', type=str, nargs='+', help="new colors, must be same length as original colors")
    args = parser.parse_args()
    colorType = 'hex'
    for i, color in enumerate(args.colors):
        if ',' in color:
            colors = color.split(',')
            colors = list(map(int, colors))
            args.colors[i] = colors
            colorType = 'rgb'

    changeFontColor = ChangeFontColor(args.path, args.colors, colorType)
