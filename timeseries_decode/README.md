# Time Series Decode Example

This folder contains examples for decoding time series data returned by the API.

Two versions are provided: a simple one for learning and a more complete with full error handling.
Both produce the same output.

## Encoding format

The API time series value field is expected to be:

1. Binary values in big-endian byte order
2. Compressed bytes (`zlib`)
3. Base64 encoded text

## Examples

### Simple example

A minimal, easy-to-follow script that shows the three decoding steps directly:

```bash
uv run timeseries_decode/decode_time_series_simple.py
```

Reads `timeseries_decode/samples/sample_api_response_02.json` by default.

### Full example

A production-ready script with proper error handling, type annotations, and CLI support:

```bash
uv run timeseries_decode/decode_time_series.py
```

By default it reads:

- `timeseries_decode/samples/sample_api_response_01.json`

You can provide your own payload file:

```bash
uv run timeseries_decode/decode_time_series.py --file path/to/response.json
```

If the data contains scalars, this example ignores them.
