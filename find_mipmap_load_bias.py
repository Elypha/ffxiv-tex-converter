import os
from kaitaistruct import KaitaiStream, BytesIO
from src.parsers.mtrl import Mtrl
import struct


def process_mtrl_file(input_path, output_path):
    with open(input_path, 'rb') as f:
        data = f.read()

    io = KaitaiStream(BytesIO(data))
    mtrl = Mtrl(io)

    constant_id = 0x39551220
    target_constant = None
    for sc in mtrl.shader_constants:
        if sc.constant_id == constant_id:
            target_constant = sc
            break

    if target_constant is not None:
        # Calculate the correct offset for the shader constant data
        shader_data_start = (mtrl._io.size() - mtrl.shader_info.shader_constants_data_size)
        actual_offset = shader_data_start + target_constant.offset

        # Read the current value
        current_value = struct.unpack('<f', data[actual_offset:actual_offset + 4])[0]

        if current_value != 0.0:
            # Modify the shader constant only if it's not already 0
            new_value = 0.0
            new_bytes = struct.pack('<f', new_value)
            data = (
                    data[:actual_offset] +
                    new_bytes +
                    data[actual_offset + 4:]
            )

            # Write the modified data to the output file
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, 'wb') as f:
                f.write(data)

            return True  # Indicate that the file was modified

    return False  # Indicate that the file was not modified


def process_directory(input_dir, output_dir):
    for root, dirs, files in os.walk(input_dir):
        for file in files:
            if file.endswith('.mtrl'):
                input_path = os.path.join(root, file)
                relative_path = os.path.relpath(input_path, input_dir)
                output_path = os.path.join(output_dir, relative_path)
                try:
                    was_modified = process_mtrl_file(input_path, output_path)
                    if was_modified:
                        print(f"Modified: {input_path} -> {output_path}")
                    else:
                        print(f"Skipped (already 0 or constant not found): {input_path}")
                except Exception as e:
                    print(f"Error processing {input_path}: {str(e)}")


# Set your input and output directories here
input_directory = "material_input"
output_directory = "material_output"

process_directory(input_directory, output_directory)