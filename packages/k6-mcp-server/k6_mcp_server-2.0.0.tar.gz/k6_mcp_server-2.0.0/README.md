# K6 MCP Server

A Model Context Protocol (MCP) server for running k6 load tests and stress tests.

## Features

- **Load Testing**: Run k6 load tests with configurable virtual users, duration, and request parameters
- **Stress Testing**: Run multi-stage stress tests to gradually increase load
- **JSON Results**: Get detailed test results in JSON format
- **Flexible Configuration**: Support for custom HTTP methods, headers, body, and thresholds

## Prerequisites

- Python 3.10 or higher
- k6 installed on your system ([Installation Guide](https://k6.io/docs/get-started/installation/))

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the server:
```bash
python index.py
```

## Tools

### run_k6_load_test

Run a k6 load test against a specific URL.

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

### run_k6_stress_test

Run a k6 stress test with multiple stages to gradually increase load.

**Parameters:**
- `url` (required): Target URL for the stress test
- `stages` (optional): Array of stages with duration and target VUs
- `method` (optional): HTTP method (default: "GET")
- `headers` (optional): HTTP headers object
- `body` (optional): Request body for POST/PUT requests
- `thresholds` (optional): k6 thresholds for pass/fail criteria

**Example:**
```json
{
  "url": "https://httpbin.org/get",
  "stages": [
    {"duration": "2m", "target": 10},
    {"duration": "5m", "target": 20},
    {"duration": "2m", "target": 0}
  ]
}
```

## License

MIT License
