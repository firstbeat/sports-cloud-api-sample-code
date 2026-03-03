# Time Series Decode Example

This folder contains an example for decoding time series data returned by the API.

## Encoding format

The API time series value field is expected to be:

1. Binary values in big-endian byte order
2. Compressed bytes (`zlib`)
3. Base64 encoded text

## Run

```bash
uv run python timeseries_decode/decode_time_series.py
```

By default it reads:

- `timeseries_decode/samples/sample_api_response_01.json`

You can provide your own payload file:

```bash
uv run python timeseries_decode/decode_time_series.py --file path/to/response.json
```

