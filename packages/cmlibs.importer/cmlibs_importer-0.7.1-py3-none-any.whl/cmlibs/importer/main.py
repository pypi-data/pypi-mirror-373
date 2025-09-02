import argparse
import importlib
import os.path
import pkgutil
import sys

import cmlibs.importer as imp

from cmlibs.importer import celldensity
from cmlibs.importer import colonhrm
from cmlibs.importer import colonmanometry
from cmlibs.importer import dxf
from cmlibs.importer import mbfxml
from cmlibs.importer import obj
from cmlibs.importer import ply
from cmlibs.importer import ragpdata
from cmlibs.importer import stl
from cmlibs.importer import svg
from cmlibs.importer import xyz

from cmlibs.importer.errors import ImporterImportError


def _is_importer_module(mod):
    if hasattr(mod, 'identifier') and hasattr(mod, 'import_data') and hasattr(mod, 'import_data_into_region') and hasattr(mod, 'parameters'):
        return True
    return False


def available_importers():
    pkgpath = os.path.dirname(imp.__file__)
    package_names = [name for _, name, _ in pkgutil.iter_modules([pkgpath])]
    importers = []
    for name in package_names:
        t = importlib.import_module(f'cmlibs.importer.{name}')
        if _is_importer_module(t):
            importers.append(t.identifier())
    return importers


def import_data(importer, inputs, working_directory):
    t = importlib.import_module(f'cmlibs.importer.{importer.lower()}')
    if _is_importer_module(t):
        return t.import_data(inputs, working_directory)

    raise ImporterImportError(f"Unknown importer: {importer}")


def import_parameters(importer):
    t = importlib.import_module(f'cmlibs.importer.{importer.lower()}')
    if _is_importer_module(t):
        return t.parameters()

    raise ImporterImportError(f"Unknown importer: {importer}")


def main():
    parser = argparse.ArgumentParser(description='Import data into Zinc.')
    parser.add_argument("-o", "--output", default=os.curdir, help='output directory, default is the current directory.')
    parser.add_argument("-l", "--list", help="list available importers", action='store_true')
    subparsers = parser.add_subparsers(dest="importer", help="types of importer")

    ragp_parser = subparsers.add_parser(ragpdata.identifier())
    ragp_parser.add_argument("mbf_xml_file", nargs=1, help="MBF XML marker file.")
    ragp_parser.add_argument("csv_file", nargs=1, help="CSV file of gene, marker name, value matrix.")

    hrm_parser = subparsers.add_parser(colonhrm.identifier())
    hrm_parser.add_argument("colon_hrm_file", help="Colon HRM tab separated values file.")

    cd_parser = subparsers.add_parser(celldensity.identifier())
    cd_parser.add_argument("cell_density_file", help="Cell density csv file.")

    cm_parser = subparsers.add_parser(colonmanometry.identifier())
    cm_parser.add_argument("colon_manometry_file", help="Colon manometry file.")

    dxf_parser = subparsers.add_parser(dxf.identifier())
    dxf_parser.add_argument("dxf_file", help="DXF file.")

    mbfxml_parser = subparsers.add_parser(mbfxml.identifier())
    mbfxml_parser.add_argument("mbfxml_file", help="MBF XML file.")

    obj_parser = subparsers.add_parser(obj.identifier())
    obj_parser.add_argument("obj_file", help="OBJ file.")

    ply_parser = subparsers.add_parser(ply.identifier())
    ply_parser.add_argument("ply_file", help="PLY file.")

    stl_parser = subparsers.add_parser(stl.identifier())
    stl_parser.add_argument("cell_density_file", help="STL file.")

    svg_parser = subparsers.add_parser(svg.identifier())
    svg_parser.add_argument("svg_file", help="SVG file.")

    xyz_parser = subparsers.add_parser(xyz.identifier())
    xyz_parser.add_argument("xyz_file", help="XYZ file.")

    args = parser.parse_args()

    if args.list:
        print("Available importers:")
        for id_ in available_importers():
            print(f" - {id_}")
    else:
        if args.output and not os.path.isdir(args.output):
            sys.exit(1)

        inputs = []
        if args.importer == ragpdata.identifier():
            inputs.extend(args.mbf_xml_file)
            inputs.extend(args.csv_file)
        elif args.importer == colonhrm.identifier():
            inputs.extend(args.colon_hrm_file)
        elif args.importer == celldensity.identifier():
            inputs.extend(args.cell_density_file)
        elif args.importer == colonmanometry.identifier():
            inputs.extend(args.colon_manometry_file)
        elif args.importer == dxf.identifier():
            inputs.extend(args.dxf_file)
        elif args.importer == mbfxml.identifier():
            inputs.extend(args.mbfxml_file)
        elif args.importer == obj.identifier():
            inputs.extend(args.obj_file)
        elif args.importer == ply.identifier():
            inputs.extend(args.ply_file)
        elif args.importer == stl.identifier():
            inputs.extend(args.stl_file)
        elif args.importer == svg.identifier():
            inputs.extend(args.svg_file)
        elif args.importer == xyz.identifier():
            inputs.extend(args.xyz_file)

        import_data(args.importer, inputs, args.output)


if __name__ == "__main__":
    main()
