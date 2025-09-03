import argparse
import pathlib
from xml.dom import minidom

import gmsh
import numpy as np
from svg.path import parse_path
from svg.path import Close, CubicBezier, Line, Move


def parse_svg_into_steps(path: str):
    doc = minidom.parse(path)
    path_str = doc.getElementsByTagName("path")[0].getAttribute("d")
    doc.unlink()
    return parse_path(path_str)


def convert_svg_to_stl(svg_path, thickness=1, definition=5, skip=0, show=False, output_path=None):
    steps = parse_svg_into_steps(svg_path)

    shapes = []
    shape = []
    for step in steps:
        if isinstance(step, Line):
            shape.append([step.start.real, step.start.imag])
        elif isinstance(step, Close):
            shapes.append(shape)
            shape = []
        elif not isinstance(step, Move):
            for t in np.linspace(0, 1, definition, endpoint=False):
                p = step.point(t)
                shape.append([p.real, p.imag])

    # Calculate bounding box with padding
    all_points = np.vstack(shapes)
    x_min, y_min = all_points.min(axis=0)
    x_max, y_max = all_points.max(axis=0)
    x_pad = 0.1 * (x_max - x_min)
    y_pad = 0.1 * (y_max - y_min)
    corners = [
        [x_min - x_pad, y_min - y_pad],
        [x_min - x_pad, y_max + y_pad],
        [x_max + x_pad, y_max + y_pad],
        [x_max + x_pad, y_min - y_pad],
    ]
    shapes.append(corners)

    # Gmsh geometry creation
    gmsh.initialize()
    gmsh.model.add("svg_model")

    z_floor, z_ceiling = 0, thickness
    factory = gmsh.model.geo

    for shape in shapes[skip:]:
        # Create points and lines for floor and ceiling
        floor_points = [factory.addPoint(x, y, z_floor) for x, y in shape]
        ceiling_points = [factory.addPoint(x, y, z_ceiling) for x, y in shape]
        
        # Create connecting lines
        floor_lines = [factory.addLine(floor_points[i], floor_points[(i+1)%len(shape)]) 
                      for i in range(len(shape))]
        ceiling_lines = [factory.addLine(ceiling_points[i], ceiling_points[(i+1)%len(shape)]) 
                        for i in range(len(shape))]
        wall_lines = [factory.addLine(floor_points[i], ceiling_points[i]) 
                     for i in range(len(shape))]

        # Create surfaces
        for i in range(len(shape)):
            wall_loop = factory.addCurveLoop([
                floor_lines[i],
                wall_lines[(i+1)%len(shape)],
                -ceiling_lines[i],
                -wall_lines[i]
            ])
            factory.addPlaneSurface([wall_loop])

    # Create final surfaces
    floor_loops = [factory.addCurveLoop([factory.addLine(
        factory.addPoint(x, y, z_floor), 
        factory.addPoint(shape[(i+1)%len(shape)][0], shape[(i+1)%len(shape)][1], z_floor)
    ) for i, (x, y) in enumerate(shape)]) for shape in shapes[skip:]]
    
    ceiling_loops = [factory.addCurveLoop([factory.addLine(
        factory.addPoint(x, y, z_ceiling), 
        factory.addPoint(shape[(i+1)%len(shape)][0], shape[(i+1)%len(shape)][1], z_ceiling)
    ) for i, (x, y) in enumerate(shape)]) for shape in shapes[skip:]]

    factory.addPlaneSurface(floor_loops)
    factory.addPlaneSurface(ceiling_loops)

    # Generate mesh and save
    factory.synchronize()
    gmsh.model.mesh.generate(3)
    
    output_path = output_path or pathlib.Path(svg_path).with_suffix(".stl")
    gmsh.write(str(output_path))

    if show:
        gmsh.fltk.run()
    
    gmsh.finalize()


def main():
    parser = argparse.ArgumentParser(description="Convert SVG to STL")
    parser.add_argument("svg_path", help="Path to SVG file")
    parser.add_argument("-t", "--thickness", type=float, default=1.0)
    parser.add_argument("-d", "--definition", type=int, default=5)
    parser.add_argument("-s", "--skip", type=int, default=0)
    parser.add_argument("--show", action="store_true")
    parser.add_argument("-o", "--output")
    
    args = parser.parse_args()
    convert_svg_to_stl(
        svg_path=args.svg_path,
        thickness=args.thickness,
        definition=args.definition,
        skip=args.skip,
        show=args.show,
        output_path=args.output
    )


if __name__ == "__main__":
    main()