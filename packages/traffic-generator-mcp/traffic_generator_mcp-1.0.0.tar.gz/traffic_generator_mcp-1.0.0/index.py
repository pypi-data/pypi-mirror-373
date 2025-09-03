import datetime
import json
import logging
import os
import subprocess
import tempfile
import threading
import uuid
from typing import Any, Dict, List, Optional

import boto3
import mcp.server.stdio
import mcp.types as types
from mcp.server.fastmcp import FastMCP

# Configure logging
logging.basicConfig(level=logging.WARNING)  # Reduce logging verbosity
logger = logging.getLogger(__name__)

mcp = FastMCP("k6-mcp-server")

now = datetime.datetime.now()
iso_string = now.isoformat()
# Global storage for running tests
running_tests = {}
test_results = {}
test_processes = {}


def _run_k6_command_background(
    test_id: str, cmd: List[str], script_path: str, json_output_path: str
):
    """Run k6 command in background thread"""
    try:
        logger.info(f"Starting background k6 test {test_id}")
        running_tests[test_id]["status"] = "running"
        running_tests[test_id]["start_time"] = now

        # Run k6 command
        result = _run_k6_command(cmd, script_path, timeout=1800)  # 30 minutes max

        if result.returncode == 0:
            # Read JSON output
            try:
                with open(json_output_path, "r") as f:
                    json_output = f.read()
                test_results[test_id] = _parse_k6_output(json_output)
                running_tests[test_id]["status"] = "completed"
            except Exception as e:
                running_tests[test_id]["status"] = "failed"
                running_tests[test_id]["error"] = f"Failed to parse results: {str(e)}"
        else:
            running_tests[test_id]["status"] = "failed"
            running_tests[test_id]["error"] = result.stderr

    except Exception as e:
        running_tests[test_id]["status"] = "failed"
        running_tests[test_id]["error"] = str(e)
    finally:
        running_tests[test_id]["end_time"] = now
        # Clean up files
        for path in [script_path, json_output_path]:
            if os.path.exists(path):
                try:
                    os.unlink(path)
                except:
                    pass


def _run_k6_command(
    cmd: List[str],
    script_path: str,
    timeout: int = 900,  # Default 15 minutes
) -> subprocess.CompletedProcess:
    """Run k6 command either directly or via Docker with extended timeout"""
    # Try direct k6 first
    try:
        result = subprocess.run(
            ["k6", "version"], capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            # k6 is installed directly
            logger.info(
                f"Using direct k6 installation, timeout set to {timeout} seconds"
            )
            return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    # Fall back to Docker
    try:
        # Check if Docker is available
        subprocess.run(
            ["docker", "--version"],
            capture_output=True,
            text=True,
            check=True,
            timeout=10,
        )

        # Convert k6 command to Docker command
        # Mount the script file and run k6 in container
        script_dir = os.path.dirname(script_path)
        script_name = os.path.basename(script_path)

        docker_cmd = [
            "docker",
            "run",
            "--rm",
            "-v",
            f"{script_dir}:/scripts",
            "grafana/k6:latest",
        ]

        # Replace k6 command parts
        k6_args = cmd[1:]  # Remove 'k6' from the beginning

        # Handle --out json=filepath for Docker
        for i, arg in enumerate(k6_args):
            if arg == "--out" and i + 1 < len(k6_args):
                next_arg = k6_args[i + 1]
                if next_arg.startswith("json="):
                    # Extract the file path
                    json_path = next_arg.split("=", 1)[1]
                    if json_path.startswith("/"):
                        # Absolute path - mount the directory and adjust path
                        json_dir = os.path.dirname(json_path)
                        json_filename = os.path.basename(json_path)
                        # Add volume mount for JSON output directory
                        docker_cmd.extend(["-v", f"{json_dir}:/json_output"])
                        k6_args[i + 1] = f"json=/json_output/{json_filename}"
            elif arg == script_path:
                k6_args[i] = f"/scripts/{script_name}"

        docker_cmd.extend(k6_args)

        logger.info(f"Using Docker k6, timeout set to {timeout} seconds")
        return subprocess.run(
            docker_cmd, capture_output=True, text=True, timeout=timeout
        )

    except (
        FileNotFoundError,
        subprocess.CalledProcessError,
        subprocess.TimeoutExpired,
    ):
        raise Exception(
            "Neither k6 nor Docker is available. Please install k6 or Docker."
        )


def _check_k6_installed() -> bool:
    """Check if k6 is installed on the system or Docker is available"""
    # First check if k6 is installed directly
    try:
        result = subprocess.run(["k6", "version"], capture_output=True, text=True)
        if result.returncode == 0:
            return True
    except FileNotFoundError:
        pass

    # If k6 is not installed, check if Docker is available
    try:
        result = subprocess.run(["docker", "--version"], capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False


@mcp.tool()
def start_k6_load_test(
    url: str,
    vus: int = 10,
    duration: str = "30s",
    rps: Optional[int] = None,
    method: str = "GET",
    headers: Optional[Dict[str, str]] = None,
    body: Optional[Any] = None,
    thresholds: Optional[Dict[str, List[str]]] = None,
) -> types.CallToolResult:
    """Start k6 load test in background and return test ID for monitoring

    Args:
        url: Target URL to test
        vus: Number of virtual users (default: 10)
        duration: Test duration like "30s", "5m" (default: "30s")
        rps: Requests per second limit (optional)
        method: HTTP method - GET, POST, PUT, DELETE (default: "GET")
        headers: HTTP headers as dict (optional)
        body: Request body - accepts string, dict, or any JSON-serializable object (optional)
        thresholds: Performance thresholds as dict (optional)

    Example:
        # Simple GET test
        start_k6_load_test("https://api.example.com/health")

        # POST with JSON object
        start_k6_load_test(
            url="https://api.example.com/data",
            method="POST",
            headers={"Content-Type": "application/json"},
            body={"message": "test data", "timestamp": "2024-01-01"}
        )

        # POST with JSON string
        start_k6_load_test(
            url="https://api.example.com/data",
            method="POST",
            headers={"Content-Type": "application/json"},
            body='{"message": "test data", "timestamp": "2024-01-01"}'
        )
    """

    if not _check_k6_installed():
        raise Exception(
            "Neither k6 nor Docker is installed. Please install k6 or Docker."
        )

    # Generate unique test ID
    test_id = str(uuid.uuid4())[:8]

    try:
        # Create k6 script
        k6_script = _generate_k6_script(
            url=url,
            method=method,
            headers=headers or {},
            body=body,
            thresholds=thresholds or {},
        )

        # Write script to temporary file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".js", delete=False) as f:
            f.write(k6_script)
            script_path = f.name

        # Create temporary file for JSON output
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as json_file:
            json_output_path = json_file.name

        # Build k6 command
        cmd = ["k6", "run", "--out", f"json={json_output_path}"]
        cmd.extend(["--vus", str(vus)])
        cmd.extend(["--duration", duration])
        if rps:
            cmd.extend(["--rps", str(rps)])
        cmd.append(script_path)

        # Initialize test tracking
        running_tests[test_id] = {
            "status": "starting",
            "url": url,
            "vus": vus,
            "duration": duration,
            "method": method,
            "created_time": now,
            "command": " ".join(cmd),
        }

        # Start background thread
        thread = threading.Thread(
            target=_run_k6_command_background,
            args=(test_id, cmd, script_path, json_output_path),
        )
        thread.daemon = True
        thread.start()

        result_text = f"""K6 Load Test Started Successfully!

Test ID: {test_id}
URL: {url}
Virtual Users: {vus}
Duration: {duration}
Method: {method}

Use 'check_k6_test_status' with test_id '{test_id}' to monitor progress.
Use 'get_k6_test_results' with test_id '{test_id}' to get results when completed."""

        return types.CallToolResult(
            content=[types.TextContent(type="text", text=result_text)]
        )

    except Exception as error:
        raise Exception(f"Failed to start k6 load test: {str(error)}")


@mcp.tool()
def check_k6_test_status(test_id: str) -> types.CallToolResult:
    """Check the status of a running k6 test"""

    if test_id not in running_tests:
        raise Exception(f"Test ID '{test_id}' not found")

    test_info = running_tests[test_id]
    status = test_info["status"]

    result_text = f"""K6 Test Status: {test_id}

Status: {status.upper()}
URL: {test_info["url"]}
VUs: {test_info["vus"]}
Duration: {test_info["duration"]}
Created: {test_info["created_time"]}"""

    if "start_time" in test_info:
        result_text += f"\nStarted: {test_info['start_time']}"

    if "end_time" in test_info:
        result_text += f"\nEnded: {test_info['end_time']}"

    if status == "failed" and "error" in test_info:
        result_text += f"\nError: {test_info['error']}"

    if status == "completed":
        result_text += (
            "\n\nTest completed! Use 'get_k6_test_results' to view detailed results."
        )

    return types.CallToolResult(
        content=[types.TextContent(type="text", text=result_text)]
    )


@mcp.tool()
def get_k6_test_results(test_id: str) -> types.CallToolResult:
    """Get detailed results of a completed k6 test"""

    if test_id not in running_tests:
        raise Exception(f"Test ID '{test_id}' not found")

    if running_tests[test_id]["status"] != "completed":
        raise Exception(
            f"Test '{test_id}' is not completed yet. Current status: {running_tests[test_id]['status']}"
        )

    if test_id not in test_results:
        raise Exception(f"Results for test '{test_id}' not available")

    results = test_results[test_id]
    test_info = running_tests[test_id]

    result_text = f"""K6 Test Results: {test_id}

Test Configuration:
- URL: {test_info["url"]}
- VUs: {test_info["vus"]}
- Duration: {test_info["duration"]}
- Started: {test_info.get("start_time", "N/A")}
- Ended: {test_info.get("end_time", "N/A")}

Detailed Results:
{json.dumps(results, indent=2)}"""

    return types.CallToolResult(
        content=[types.TextContent(type="text", text=result_text)]
    )


@mcp.tool()
def invoke_amazon_msk_relay(speedup: float) -> types.CallToolResult:
    """Invoke MSK message relay Lambda function to inject messages

    Args:
        speedup: Speed multiplier for message replay (e.g., 1.0 for normal speed, 2.0 for 2x speed)
    """

    # Get environment variables
    function_name = os.getenv("RELAY_FUNCTION_NAME")
    stream_arn = os.getenv("RELAY_STREAM_ARN")
    bucket_name = os.getenv("RELAY_BUCKET_NAME")
    region = os.getenv("AWS_REGION", "us-west-2")

    if not all([function_name, stream_arn, bucket_name]):
        raise Exception(
            "Missing required environment variables: RELAY_FUNCTION_NAME, RELAY_STREAM_ARN, RELAY_BUCKET_NAME"
        )

    # Fixed payload parameters
    payload = {
        "streamArn": stream_arn,
        "producerType": "kafka",
        "bucketName": bucket_name,
        "bucketRegion": region,
        "objectPrefix": "events/",
        "speedup": speedup,
        "timestampAttributeName": "timestamp",
    }

    try:
        # Create Lambda client
        lambda_client = boto3.client("lambda", region_name=region)

        # Invoke Lambda function
        response = lambda_client.invoke(
            FunctionName=function_name, Payload=json.dumps(payload)
        )

        # Read response
        response_payload = response["Payload"].read().decode("utf-8")

        result_text = f"""MSK Message Relay Invoked Successfully!

Function: {function_name}
Stream ARN: {stream_arn}
Bucket: {bucket_name}
Speedup: {speedup}x

Response:
{response_payload}"""

        return types.CallToolResult(
            content=[types.TextContent(type="text", text=result_text)]
        )

    except Exception as error:
        raise Exception(f"Failed to invoke MSK message relay: {str(error)}")


def _generate_k6_script(
    url: str,
    method: str,
    headers: Dict[str, str],
    body: Any,
    thresholds: Dict[str, List[str]],
) -> str:
    """Generate k6 JavaScript test script"""

    # Convert headers to JavaScript object
    headers_js = json.dumps(headers) if headers else "{}"

    # Convert thresholds to JavaScript object
    thresholds_js = json.dumps(thresholds) if thresholds else "{}"

    # Handle request body - accept both string and object, always stringify
    body_js = "null"
    if body is not None:
        if isinstance(body, str):
            # If it's already a string, try to parse as JSON first
            try:
                # Parse to validate JSON, then re-stringify
                parsed = json.loads(body)
                body_js = json.dumps(json.dumps(parsed))
            except json.JSONDecodeError:
                # If not valid JSON, treat as plain string
                body_js = json.dumps(body)
        else:
            # If it's an object/dict, stringify it
            body_js = json.dumps(json.dumps(body))

    script = f"""
import http from 'k6/http';
import {{ check }} from 'k6';

export let options = {{
    thresholds: {thresholds_js}
}};

export default function() {{
    let params = {{
        headers: {headers_js}
    }};
    
    let response;
    
    if ('{method.upper()}' === 'GET') {{
        response = http.get('{url}', params);
    }} else if ('{method.upper()}' === 'POST') {{
        response = http.post('{url}', {body_js}, params);
    }} else if ('{method.upper()}' === 'PUT') {{
        response = http.put('{url}', {body_js}, params);
    }} else if ('{method.upper()}' === 'DELETE') {{
        response = http.del('{url}', {body_js}, params);
    }} else {{
        response = http.request('{method.upper()}', '{url}', {body_js}, params);
    }}
    
    check(response, {{
        'status is 200': (r) => r.status === 200,
        'response time < 500ms': (r) => r.timings.duration < 500,
    }});
}}
"""
    return script


def _parse_k6_output(output: str) -> Dict[str, Any]:
    """Parse k6 JSON output and extract key metrics"""
    lines = output.strip().split("\n")
    metrics = {}

    for line in lines:
        if line.strip():
            try:
                data = json.loads(line)
                if data.get("type") == "Point":
                    metric_name = data.get("metric")
                    if metric_name:
                        if metric_name not in metrics:
                            metrics[metric_name] = []
                        metrics[metric_name].append(
                            {
                                "timestamp": data.get("data", {}).get("time"),
                                "value": data.get("data", {}).get("value"),
                                "tags": data.get("data", {}).get("tags", {}),
                            }
                        )
            except json.JSONDecodeError:
                # Skip non-JSON lines (like k6 summary output)
                continue

    # Calculate summary statistics
    summary = {}
    for metric_name, values in metrics.items():
        if values:
            numeric_values = [
                v["value"] for v in values if isinstance(v["value"], (int, float))
            ]
            if numeric_values:
                summary[metric_name] = {
                    "count": len(numeric_values),
                    "min": min(numeric_values),
                    "max": max(numeric_values),
                    "avg": sum(numeric_values) / len(numeric_values),
                    "values": values[:10],  # Include first 10 data points
                }

    return {
        "summary": summary,
        "total_data_points": sum(len(values) for values in metrics.values()),
    }


def handle_list_tools() -> List[types.Tool]:
    """List available tools"""
    logger.info("Handling list_tools request")

    tools = [
        types.Tool(
            name="start_k6_load_test",
            description="Start k6 load test in background and return test ID for monitoring",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "Target URL for the load test",
                    },
                    "vus": {
                        "type": "integer",
                        "description": "Number of virtual users (default: 10)",
                        "default": 10,
                    },
                    "duration": {
                        "type": "string",
                        "description": "Test duration (e.g., '30s', '5m', '1h') (default: '30s')",
                        "default": "30s",
                    },
                    "rps": {
                        "type": "integer",
                        "description": "Requests per second limit (optional)",
                    },
                    "method": {
                        "type": "string",
                        "description": "HTTP method (GET, POST, PUT, DELETE, etc.) (default: 'GET')",
                        "default": "GET",
                    },
                    "headers": {
                        "type": "object",
                        "description": "HTTP headers to include in requests",
                    },
                    "body": {
                        "description": "Request body - accepts string, dict, or any JSON-serializable object",
                    },
                    "thresholds": {
                        "type": "object",
                        "description": "k6 thresholds for pass/fail criteria",
                    },
                },
                "required": ["url"],
            },
        ),
        types.Tool(
            name="check_k6_test_status",
            description="Check the status of a running k6 test",
            inputSchema={
                "type": "object",
                "properties": {
                    "test_id": {
                        "type": "string",
                        "description": "Test ID returned by start_k6_load_test",
                    },
                },
                "required": ["test_id"],
            },
        ),
        types.Tool(
            name="get_k6_test_results",
            description="Get detailed results of a completed k6 test",
            inputSchema={
                "type": "object",
                "properties": {
                    "test_id": {
                        "type": "string",
                        "description": "Test ID returned by start_k6_load_test",
                    },
                },
                "required": ["test_id"],
            },
        ),
        types.Tool(
            name="invoke_amazon_msk_relay",
            description="Invoke MSK message relay Lambda function to inject messages",
            inputSchema={
                "type": "object",
                "properties": {
                    "speedup": {
                        "type": "number",
                        "description": "Speed multiplier for message replay (e.g., 1.0 for normal speed, 2.0 for 2x speed)",
                    },
                },
                "required": ["speedup"],
            },
        ),
    ]

    # Validate Tools
    for i, tool in enumerate(tools):
        logger.info(f"Tool {i}: {type(tool)} - {getattr(tool, 'name', 'NO_NAME')}")
        if not hasattr(tool, "name"):
            logger.error(f"Tool missing name attribute: {tool}")
            raise ValueError(f"Invalid tool definition: {tool}")

    logger.info(f"Returning {len(tools)} tools")
    return tools


def run_server():
    """Run the MCP server"""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    run_server()
