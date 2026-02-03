# Quickstart Examples

This quick start script contains working but heavily simplified example of the API usage. The purpose of this script is to get you started fast and to understand how to API works. 

If you have working API access, the script should run as is. 

## Files

- `cloud-api-example.py` - Interactive example with account/athlete selection
- `cloudapiclient.py` - Reusable API client class with pagination and retry logic

## Running

Set credentials as environment variables:

```bash
export FIRSTBEAT_SHARED_SECRET="your-secret"
export FIRSTBEAT_CONSUMER_ID="your-consumer-id"
```

Run with uv (recommended):

```bash
uv run quickstart/cloud-api-example.py
```

Or with command-line arguments:

```bash
uv run quickstart/cloud-api-example.py --shared-secret <secret> --consumer-id <id>
```