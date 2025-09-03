# Traffic Generator MCP Server

A Model Context Protocol (MCP) server for running k6 load tests and invoking AWS MSK message relay functions.

## Features

- **Load Testing**: Run k6 load tests with configurable virtual users, duration, and request parameters
- **Test Monitoring**: Check status and get results of running tests
- **MSK Message Relay**: Invoke AWS Lambda functions to inject messages into MSK streams
- **JSON Results**: Get detailed test results in JSON format
- **Flexible Configuration**: Support for custom HTTP methods, headers, body, and thresholds

## Prerequisites

- Python 3.10 or higher
- k6 installed on your system ([Installation Guide](https://k6.io/docs/get-started/installation/))
- AWS credentials configured for MSK message relay functionality

## Usage

### \*.json file

```json
{
  "mcpServers": {
    "traffic-generator-mcp": {
      "command": "uvx",
      "args": ["traffic-generator-mcp@latest"],
      "env": {
        "RELAY_FUNCTION_NAME": "function-name",
        "RELAY_STREAM_ARN": "stream-arn",
        "RELAY_BUCKET_NAME": "bucket-name"
      }
    }
  }
}
```

### Strands Agent SDK

```python
traffic_generator_mcp_client = MCPClient(
    lambda: stdio_client(
        StdioServerParameters(
            command="uvx",
            args=["traffic-generator-mcp@2.2.0"],
            env={
                **aws_env,
                "RELAY_FUNCTION_NAME": "function-name",
                "RELAY_STREAM_ARN": "stream-arn",
                "RELAY_BUCKET_NAME": "bucket-name"
            },
        )
    )
)

traffic_generator_mcp_client.start()

agent = Agent(
    model,
    system_prompt,
    tools=[traffic_generator_mcp_client.list_tools_sync()],
)
```

## Tools

### start_k6_load_test

Start a k6 load test in background and return test ID for monitoring.

**Parameters:**

- `url` (required): Target URL for the load test
- `vus` (optional): Number of virtual users (default: 10)
- `duration` (optional): Test duration (default: "30s")
- `rps` (optional): Requests per second limit
- `method` (optional): HTTP method (default: "GET")
- `headers` (optional): HTTP headers object
- `body` (optional): Request body for POST/PUT requests
- `thresholds` (optional): k6 thresholds for pass/fail criteria

**Example:**

```json
{
  "url": "https://httpbin.org/get",
  "vus": 20,
  "duration": "1m",
  "method": "GET",
  "headers": {
    "User-Agent": "k6-test"
  }
}
```

### check_k6_test_status

Check the status of a running k6 test.

**Parameters:**

- `test_id` (required): Test ID returned by start_k6_load_test

### get_k6_test_results

Get detailed results of a completed k6 test.

**Parameters:**

- `test_id` (required): Test ID returned by start_k6_load_test

### invoke_msk_message_relay

Invoke MSK message relay Lambda function to inject messages into MSK streams.

**Parameters:**

- `speedup` (required): Speed multiplier for message replay (e.g., 1.0 for normal speed, 2.0 for 2x speed)

**Example:**

```json
{
  "speedup": 2.0
}
```

**Environment Variables Required:**

- `RELAY_FUNCTION_NAME`: Lambda function name
- `RELAY_STREAM_ARN`: MSK stream ARN
- `RELAY_BUCKET_NAME`: S3 bucket name containing message data

## License

MIT License
