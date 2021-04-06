import math
import argparse
import shapely.geometry as sg

try:
    import crayons
except:
    pass

from pcbflow import *

SVG_BOUNDARY = 5


def max_bounds(bounds):
    mbounds = [1e18, 1e18, -1e18, -1e18]
    for b in bounds:
        if len(b) > 0:
            mbounds[0] = min(mbounds[0], b[0])
            mbounds[1] = min(mbounds[1], b[1])
            mbounds[2] = max(mbounds[2], b[2])
            mbounds[3] = max(mbounds[3], b[3])
    # if no valid baounds, return a safe minimum rectangle
    if mbounds[0] > mbounds[3]:
        return (-SVG_BOUNDARY, -SVG_BOUNDARY, SVG_BOUNDARY, SVG_BOUNDARY)
    # apply a small boundary margin
    mbounds = [
        mbounds[0] - SVG_BOUNDARY,
        mbounds[1] - SVG_BOUNDARY,
        mbounds[2] + SVG_BOUNDARY,
        mbounds[3] + SVG_BOUNDARY,
    ]
    return mbounds


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "library", metavar="library", type=str, help="EAGLE Library file"
    )
    parser.add_argument(
        "-p", "--part", action="store", default=None, help="Select a part from library"
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        default=False,
        help="Show verbose entities of part",
    )
    parser.add_argument(
        "-s",
        "--svg",
        action="store_true",
        default=False,
        help="Export part to SVG file",
    )
    args = parser.parse_args()
    argsd = vars(args)

    if argsd["part"] is not None:
        show_lbr_package(argsd["library"], argsd["part"])
        brd = Board((100, 100))
        brd.drc.mask_holes = True
        brd.drc.hole_mask = MILS(10)
        try:
            part = EaglePart(
                brd.DC((50, 50)),
                libraryfile=argsd["library"],
                partname=argsd["part"],
                debug=argsd["verbose"],
            )
        except ValueError:
            print(
                crayons.red("Part ")
                + argsd["part"]
                + crayons.red(" was not found in ")
                + argsd["library"]
            )
            exit()
        b = []
        for layer in ["GTO", "GTL", "GTS", "GTP"]:
            obj = brd.layers[layer].preview()
            b.append(obj.bounds)
        bounds = max_bounds(b)
        g = sg.box(*bounds)
        brd.layers["GML"].add(g)
        if argsd["svg"]:
            print("Exporting %s in %s..." % (argsd["part"], argsd["library"]))
            svg_write(brd, argsd["part"] + ".svg")
            print(
                crayons.green("%s exported to %s.svg" % (argsd["part"], argsd["part"]))
            )
    else:
        print(
            "Package list of Eagle library " + crayons.green("%s:" % (argsd["library"]))
        )
        n = list_lbr_packages(argsd["library"])
        print(crayons.green("%d packages found in %s" % (n, argsd["library"])))