import gc
import os
from multiprocessing import Pool
from pathlib import Path
from struct import pack

import numpy
from numpy import ushort
from tqdm import tqdm

from src.parsers.tex import Tex
from src.parsers.dds import Dds

lod_offset = numpy.array([0, 1, 2], dtype=numpy.int32)


def get_tex_mipmap_length_format(dds):
    height = dds.hdr.height
    width = dds.hdr.width
    fourcc = dds.hdr.ddspf.fourcc
    # potentially might put in BC4 and BC5 (ATI1, ATI2)
    if fourcc == Dds.DdsPixelformat.PixelFormats.dxt1:
        return int(height * width // 2)
    if fourcc == Dds.DdsPixelformat.PixelFormats.dxt3 or fourcc == Dds.DdsPixelformat.PixelFormats.dxt5:
        return int(height * width * 2)
    if fourcc == Dds.DdsPixelformat.PixelFormats.none:
        return int(height * width * 4)
    if fourcc == Dds.DdsPixelformat.PixelFormats.dx10:
        if dds.hdr_dxt10.dxgi_format == Dds.HeaderDxt10.DxgiFormats.dxgi_format_bc7_unorm \
                or dds.hdr_dxt10.dxgi_format == Dds.HeaderDxt10.DxgiFormats.dxgi_format_bc3_unorm \
                or dds.hdr_dxt10.dxgi_format == Dds.HeaderDxt10.DxgiFormats.dxgi_format_bc2_unorm:
            return int(height * width * 2)
        if dds.hdr_dxt10.dxgi_format == Dds.HeaderDxt10.DxgiFormats.dxgi_format_bc1_unorm:
            return int(height * width // 2)
        if dds.hdr_dxt10.dxgi_format == Dds.HeaderDxt10.DxgiFormats.dxgi_format_b8g8r8a8_unorm:
            return int(height * width * 4)
    else:
        return None


def get_mipmap_offsets(mipmap_length, mipmap_count):
    offset_array = numpy.zeros(13, dtype=numpy.int32)
    offset = 80
    j = 0
    try:
        for i in range(mipmap_count):
            offset_array[j] = offset
            offset += mipmap_length
            mipmap_length = max(16, mipmap_length >> 2)
            j += 1
        return offset_array
    except IndexError as e:
        raise SystemExit(
            'Image has too many mipmaps. Mipmap amount: ' + str(mipmap_count) + '. Check last \'given\' image.\nToo '
                                                                                'many mipmaps can be caused by:\n1) '
                                                                                'Having too large an image. '
                                                                                'TEX supports up to 4096x4096 '
                                                                                'resolution *only* if you are using '
                                                                                'mipmaps.\n2) A broken cubemap. Check '
                                                                                'if image ends in \'_e\' or \'_f\'. '
                                                                                'You cannot import cubemaps anyway, '
                                                                                'so get rid of it.\n 3) I don\'t '
                                                                                'know.') from e


def get_tex_offset_array(dds):
    tex_mipmap_length = get_tex_mipmap_length_format(dds)
    tex_offset_array = get_mipmap_offsets(tex_mipmap_length, dds.hdr.mipmap_count)
    return tex_offset_array


def get_tex_attribute():
    return Tex.Header.Attribute.texture_type_2d.value


def get_tex_format(dds):
    fourcc = dds.hdr.ddspf.fourcc
    dxgi_format = dds.hdr_dxt10.dxgi_format
    dds_dxgi = Dds.HeaderDxt10.DxgiFormats
    tex_tf = Tex.Header.TextureFormat
    ddspf_pf = Dds.DdsPixelformat.PixelFormats
    if fourcc == ddspf_pf.dxt1:
        return tex_tf.dxt1.value
    if fourcc == ddspf_pf.dxt3:
        return tex_tf.dxt3.value
    if fourcc == ddspf_pf.dxt5:
        return tex_tf.dxt5.value
    if fourcc == ddspf_pf.dx10:
        if dxgi_format == dds_dxgi.dxgi_format_bc7_unorm:
            return tex_tf.bc7.value
        if dxgi_format == dds_dxgi.dxgi_format_bc3_unorm:
            return tex_tf.dxt5.value
        if dxgi_format == dds_dxgi.dxgi_format_bc2_unorm:
            return tex_tf.dxt3.value
        if dxgi_format == dds_dxgi.dxgi_format_bc1_unorm:
            return tex_tf.dxt1.value
        if dxgi_format == dds_dxgi.dxgi_format_b8g8r8a8_unorm:
            return tex_tf.b8g8r8a8.value
    if fourcc == ddspf_pf.none:
        return tex_tf.b8g8r8a8.value


def get_tex_height(dds):
    return ushort(dds.hdr.height)


def get_tex_width(dds):
    return ushort(dds.hdr.width)


def get_tex_mip_levels(dds):
    return ushort(dds.hdr.mipmap_count)


def get_tex_depth(dds):
    return ushort(dds.hdr.depth)


def get_tex_binary(path):
    dds_binary = Dds.from_file(path)
    header_info = pack('<IIHHHH', get_tex_attribute(), get_tex_format(dds_binary), get_tex_width(dds_binary),
                       get_tex_height(dds_binary), get_tex_depth(dds_binary), get_tex_mip_levels(dds_binary))
    header = (header_info + lod_offset.tobytes() + get_tex_offset_array(dds_binary).tobytes())
    body = (b''.join(dds_binary.bd.data))
    del dds_binary
    gc.collect()
    tex_binary = header + body
    return tex_binary
