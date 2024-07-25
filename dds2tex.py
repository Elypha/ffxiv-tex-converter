import argparse
import time
from pathlib import Path

from src.converters import dds_to_tex
from src.helper import process_bulk, process_single

parser = argparse.ArgumentParser(description="batch convert dds to tex")
parser.add_argument("input", help="input folder")
parser.add_argument("--output", "-o", help="output folder")
parser.add_argument("--force", "-f", action=argparse.BooleanOptionalAction, type=bool, default=False, help="force overwrite existing files")
parser.add_argument("--multiplier", "-m", type=int, default=4, help="chunk = cpu_count * multiplier; 0 = single threaded")
args = parser.parse_args()


def convert_dds2tex(params: tuple[Path, Path]):
    # read params
    file_in, file_out = params
    file_in = Path(file_in)
    file_out = Path(file_out)

    # skip
    if not args.force and file_out.exists() and file_out.stat().st_size != 0 and file_in.stat().st_mtime_ns < file_out.stat().st_mtime_ns:
        return

    # makedir
    file_out.parent.mkdir(parents=True, exist_ok=True)

    # make file
    binary = dds_to_tex.get_tex_binary(file_in.as_posix())
    with open(file_out.as_posix(), "wb") as f:
        f.write(binary)
    del binary


if __name__ == "__main__":
    t0 = time.time()
    # path
    input_folder = Path(args.input).resolve()
    if args.output:
        output_folder = Path(args.output).resolve()
    else:
        output_folder = input_folder.with_name(input_folder.name + "_tex")

    # get dds files
    dds_files = list(input_folder.rglob("*.dds"))

    # get inputs and outputs
    input_files = [i.resolve().as_posix() for i in dds_files]
    output_files = [i.with_suffix(".tex").resolve().as_posix().replace(input_folder.as_posix(), output_folder.as_posix()) for i in dds_files]
    params = list(zip(input_files, output_files))

    if args.multiplier > 0:
        process_bulk(params, convert_dds2tex, args.multiplier)
    else:
        process_single(params, convert_dds2tex)

    print(f"{len(params)}, {time.time() - t0:.2f}")
