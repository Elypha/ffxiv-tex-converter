import argparse
from pathlib import Path
from src.packageland import handler
from src.converters import dds_to_tex, tex_to_dds, dx10_to_dx9

parser = argparse.ArgumentParser(description="ffxiv-tex-converter, FFXIV TEX FILE CONVERTER")
parser.add_argument('--directory', '-d', metavar='-D', type=str, help='Initial directory to be processed.',
                    required=True)
parser.add_argument('--command', '-c', metavar='-C', type=str, help='dds-to-tex, tex-to-dds', required=True)

parser.add_argument('--parallel', '-p', metavar='-P', action=argparse.BooleanOptionalAction,
                    help='multicore processing')
parser.add_argument('--multiplier', '-m', metavar='-M', type=int, default=5,
                    help='if using multicore processing, job multiplier per core. default = 5')
args = parser.parse_args()

folder = Path(args.directory)


def read_command(command):
    if 'dds-to-tex' == command.lower():
        return do_the_thing_dds_to_tex
    if 'tex-to-dds' == command.lower():
        return do_the_thing_tex_to_dds
    if 'dx10-to-dx9' == command.lower():
        return do_the_thing_dx10_to_dx9


def do_the_thing_dds_to_tex(path):
    out_folder = Path(str(folder) + '_tex')
    out_path = Path.joinpath(out_folder, Path(*path.parts[1:]).with_suffix('.tex'))
    out_path.parent.mkdir(exist_ok=True, parents=True)
    binary = dds_to_tex.get_tex_binary(path)
    with open(out_path, 'wb') as wb:
        wb.write(binary)
    del binary


def do_the_thing_tex_to_dds(path):
    out_folder = Path(str(folder) + '_dds')
    out_path = Path.joinpath(out_folder, Path(*path.parts[1:]).with_suffix('.dds'))
    out_path.parent.mkdir(exist_ok=True, parents=True)
    binary = tex_to_dds.get_dds_binary(path)
    with open(out_path, 'wb') as wb:
        wb.write(binary)
    del binary


def do_the_thing_dx10_to_dx9(path):
    out_folder = Path(str(folder) + '_dx9')
    out_path = Path.joinpath(out_folder, Path(*path.parts[1:]).with_suffix('.dds'))
    out_path.parent.mkdir(exist_ok=True, parents=True)
    binary = dx10_to_dx9.get_dds_binary(path)
    with open(out_path, 'wb') as wb:
        wb.write(binary)
    del binary


if __name__ == '__main__':
    grabber = list(folder.glob('**/*.*'))
    function = read_command(args.command)
    if args.parallel:
        handler.parallel_process(grabber, function, args.multiplier)
    else:
        handler.solo_process(grabber, function)
