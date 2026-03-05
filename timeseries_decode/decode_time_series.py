# /// script
# dependencies = [
#   "numpy",
# ]
# ///

"""
Decode Firstbeat Sports API time series payloads.

The API time series values are encoded as:
1) binary values in big-endian byte order
2) compressed bytes (typically zlib)
3) base64 text

Usage examples:
- uv run timeseries_decode/decode_time_series.py
- uv run timeseries_decode/decode_time_series.py --file timeseries_decode/samples/sample_api_response_01.json
"""

from __future__ import annotations

import argparse
import base64
import json
import pathlib
import zlib
from typing import Any

import numpy as np


SUPPORTED_BIT_SIZES = {8, 16, 32, 64}


def _vartype_to_dtype(vartype: str, bits: int) -> np.dtype:
    """Map API ``type`` + ``bits`` metadata to a big-endian NumPy dtype.

    Args:
        vartype: Variable type from API metadata. Supported values are
            ``"float"``, ``"signed"``, and ``"unsigned"`` (case-insensitive).
        bits: Bit width of each value. Must be one of 8, 16, 32, or 64.

    Returns:
        A NumPy dtype configured for big-endian decoding.

    Raises:
        ValueError: If ``vartype`` is unsupported, ``bits`` is not a multiple
            of 8, or ``bits`` is outside supported sizes.
    """
    type_map = {
        "float": "f",
        "signed": "i",
        "unsigned": "u",
    }

    vartype_lower = vartype.lower()
    if vartype_lower not in type_map:
        raise ValueError(f"Invalid vartype '{vartype}'. Expected one of: float, signed, unsigned")

    if bits % 8 != 0:
        raise ValueError(f"Bits must be a multiple of 8, got {bits}")

    if bits not in SUPPORTED_BIT_SIZES:
        supported = ", ".join(str(size) for size in sorted(SUPPORTED_BIT_SIZES))
        raise ValueError(f"Unsupported bit width '{bits}'. Supported values: {supported}")

    type_char = type_map[vartype_lower]
    byte_count = bits // 8
    return np.dtype(f">{type_char}{byte_count}")


def _decompress_blob(blob_data: bytes) -> bytes:
    """Decompress a binary payload using zlib.

    Args:
        blob_data: Compressed bytes from the API payload.

    Returns:
        Decompressed raw bytes.

    Raises:
        ValueError: If zlib decompression fails.
    """
    try:
        return zlib.decompress(blob_data)
    except Exception as error:
        raise ValueError(f"Could not decompress payload as zlib: {error}") from error


def decode_binary_time_series(
    blob_data: bytes,
    vartype: str,
    bits: int,
) -> list[float | int]:
    """
    Decode compressed binary time series bytes into Python numeric values.

    Args:
        blob_data: Raw compressed binary data.
        vartype: One of ``"float"``, ``"signed"``, or ``"unsigned"``
            (case-insensitive).
        bits: Bit width of each value (8, 16, 32, or 64).

    Returns:
        Decoded time series as Python ``int``/``float`` values.

    Raises:
        ValueError: If dtype metadata is invalid, decompression fails, or the
            decompressed byte count is not aligned to item size.
    """
    try:
        dtype = _vartype_to_dtype(vartype=vartype, bits=bits)
        decompressed = _decompress_blob(blob_data=blob_data)

        item_size = dtype.itemsize
        if len(decompressed) % item_size != 0:
            raise ValueError(
                f"Decompressed payload length ({len(decompressed)}) is not divisible by item size ({item_size})"
            )

        return np.frombuffer(decompressed, dtype=dtype).tolist()
    except Exception as error:
        raise ValueError(f"Failed to decode binary time series: {error}") from error


def decode_base64_time_series(
    encoded_value: str,
    vartype: str,
    bits: int,
) -> list[float | int]:
    """Decode base64 text containing compressed time series data.

    This function performs base64 decode first, then delegates binary decode to
    :func:`decode_binary_time_series`.

    Args:
        encoded_value: Base64-encoded compressed payload.
        vartype: Variable type metadata (``"float"``, ``"signed"``,
            ``"unsigned"``).
        bits: Bit width of each value.

    Returns:
        Decoded time series values.

    Raises:
        ValueError: If underlying binary decode fails.
        binascii.Error: If ``encoded_value`` is not valid base64.
    """
    blob_data = base64.b64decode(encoded_value)
    return decode_binary_time_series(blob_data=blob_data, vartype=vartype, bits=bits)


def decode_measurement(
    measurement: dict[str, Any],
) -> list[dict[str, Any]]:
    """Decode all variables in a measurement-like API payload.

    Expected input shape:
    - Top-level object with a ``variables`` list.
    - Each variable includes at minimum ``value``, ``type``, and ``bits``.

    Args:
        measurement: Parsed JSON payload containing API variable definitions.

    Returns:
        A list of variable dictionaries where each entry includes all original
        keys plus a ``decoded`` key containing the decoded time series.

    Raises:
        KeyError: If required variable keys are missing.
        ValueError: If decoding fails for any variable.
    """
    variables = measurement.get("variables", [])
    decoded_variables: list[dict[str, Any]] = []

    for variable in variables:
        if "type" not in variable:
            continue
        decoded_values = decode_base64_time_series(
            encoded_value=variable["value"],
            vartype=variable["type"],
            bits=int(variable["bits"]),
        )
        decoded_variables.append({**variable, "decoded": decoded_values})

    return decoded_variables


def _print_preview(variable: dict[str, Any], max_preview: int = 10) -> None:
    """Print a compact preview of one decoded variable to stdout.

    Args:
        variable: Variable dictionary produced by :func:`decode_measurement`.
            Must include a ``decoded`` list.
        max_preview: Maximum number of decoded values to print.
    """
    values = variable["decoded"]
    preview = values[:max_preview]
    suffix = "..." if len(values) > max_preview else ""

    print(f"\nVariable: {variable.get('name', '<unknown>')}")
    print(f"Type: {variable.get('type')} | Bits: {variable.get('bits')} | Unit: {variable.get('unit', 'None')}")
    if "samplingRate" in variable:
        print(f"Sampling Rate: {variable['samplingRate']}")
    print(f"Time Series ({len(values)} values): {preview}{suffix}")


def _parse_args() -> argparse.Namespace:
    """Parse command-line arguments for the decoder CLI entrypoint.

    Returns:
        Parsed argparse namespace with a ``file`` field.
    """
    default_file = pathlib.Path(__file__).parent / "samples" / "sample_api_response_01.json"

    parser = argparse.ArgumentParser(description="Decode Firstbeat Sports API time series payload")
    parser.add_argument(
        "--file",
        type=pathlib.Path,
        default=default_file,
        help="Path to JSON payload containing a 'variables' array",
    )
    return parser.parse_args()


def main() -> None:
    """Run CLI flow: read payload JSON, decode variables, and print previews."""
    args = _parse_args()
    payload = json.loads(args.file.read_text(encoding="utf-8"))

    decoded_variables = decode_measurement(payload)
    for variable in decoded_variables:
        _print_preview(variable)


if __name__ == "__main__":
    main()
