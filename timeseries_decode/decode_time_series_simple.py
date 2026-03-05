# /// script
# dependencies = [
#   "numpy",
# ]
# ///

"""
Simple example: decode Firstbeat Sports API time series payloads.

The API time series values are encoded as:
1) binary values in big-endian byte order
2) compressed bytes (zlib)
3) base64 text

Run with:
    uv run timeseries_decode/decode_time_series_simple.py
"""

import base64
import json
import pathlib
import zlib

import numpy as np


def decode_time_series(encoded_value, data_type, bits):
    """
    Decode a base64 encoded, zlib compressed time series.

    Parameters:
    - encoded_value: Base64 encoded string of compressed data
    - data_type: Type of data ('Float', 'Signed', or 'Unsigned')
    - bits: Bit depth (8, 16, 32, or 64)

    Returns:
    - NumPy array of decoded values
    """
    # Step 1: base64 decode → get compressed bytes
    compressed = base64.b64decode(encoded_value)

    # Step 2: decompress → get raw binary values
    raw_bytes = zlib.decompress(compressed)

    # Step 3: pick the right NumPy dtype (big-endian '>' byte order)
    data_type = data_type.lower()

    if data_type == "float":
        if bits == 32:
            dtype = ">f4"   # 32-bit float
        elif bits == 64:
            dtype = ">f8"   # 64-bit float (double)
        else:
            raise ValueError(f"Unsupported bit depth for float: {bits}")
    elif data_type == "unsigned":
        if bits == 8:
            dtype = ">u1"   # unsigned 8-bit integer
        elif bits == 16:
            dtype = ">u2"   # unsigned 16-bit integer
        else:
            raise ValueError(f"Unsupported bit depth for unsigned: {bits}")
    elif data_type == "signed":
        if bits == 8:
            dtype = ">i1"   # signed 8-bit integer
        elif bits == 16:
            dtype = ">i2"   # signed 16-bit integer
        elif bits == 32:
            dtype = ">i4"   # signed 32-bit integer
        else:
            raise ValueError(f"Unsupported bit depth for signed: {bits}")
    else:
        raise ValueError(f"Unknown data type: {data_type}")

    # Step 4: interpret raw bytes as a NumPy array
    return np.frombuffer(raw_bytes, dtype=dtype)


# Load sample data
sample_file = pathlib.Path(__file__).parent / "samples" / "sample_api_response_02.json"
with open(sample_file) as f:
    data = json.load(f)

# Decode and print each variable
for variable in data["variables"]:
    name = variable["name"]
    data_type = variable["type"]
    bits = variable["bits"]
    unit = variable.get("unit", "None")
    sampling_rate = variable.get("samplingRate", "")

    print(f"\nVariable: {name}")
    print(f"Type: {data_type} | Bits: {bits} | Unit: {unit}")
    if sampling_rate:
        print(f"Sampling Rate: {sampling_rate}")

    values = decode_time_series(variable["value"], data_type, bits)
    preview = values[:10]
    suffix = "..." if len(values) > 10 else ""
    print(f"Time Series ({len(values)} values): {preview}{suffix}")
