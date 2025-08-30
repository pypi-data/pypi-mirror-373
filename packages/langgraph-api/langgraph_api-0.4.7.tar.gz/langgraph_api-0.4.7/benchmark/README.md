# K6 Performance Testing

K6 is a modern load testing tool that allows you to test the performance and reliability of your APIs. The tests in this directory are designed to validate the performance characteristics of the LangGraph API under various load conditions.

## Test Scenarios

### Available Tests

There are two modes of testing available:
1. `Burst` - Kick off a burst of /run/wait requests. 
    Available Params:
        BURST_SIZE - How many requests to run. Default: 100
2. `Ramp` - Scale up the number of /run/wait requests and then plateau.
    Available Params:
        LOAD_SIZE - How much traffic to ramp up over a 60s period. Default: 500
        LEVELS - The number of times to ramp up. Default: 2
        PLATEAU_DURATION - How long to sustain the max level of traffic in seconds. Default: 300

### Agent

We use a local benchmark agent that can be configured to run a number of different test scenarios to simulate a variety of graphs.

Available Params:
    DATA_SIZE - How many characters each message should have in a parallel or sequence node. Default: 1000
    DELAY - How long to sleep in each parallel or sequence node. Default: 0
    EXPAND - How many nodes to run in the parallel or sequence modes. Default: 50
    MODE - What configuration to run the graph. Default: single
        - `single` - Run a single node
        - `parallel` - Run EXPAND nodes in parallel
        - `sequential` - Run EXPAND nodes in sequence

## Running Tests

### Local Prerequisites

1. Install k6: https://k6.io/docs/getting-started/installation/
2. Start your LangGraph API service
3. Ensure the API is accessible at `http://localhost:9123`

### Remote Prerequisites

1. Get a LangSmith API Key: https://docs.smith.langchain.com/administration/how_to_guides/organization_management/create_account_api_key#create-an-api-key
2. The deployment jdr-benchmark is setup for this. Endpoint: https://jdr-benchmark-1cfe27c4cd375e1c999f02f186f617f6.us.langgraph.app

### Basic Usage

```bash
# Run burst test with default burst size
make benchmark-burst

# Run burst test with custom burst size
BURST_SIZE=500 make benchmark-burst

# Run ramp test with a different mode and expand size
MODE='parallel' EXPAND=100 make benchmark-ramp

# Run burst test against a deployment
BASE_URL=https://jdr-benchmark-1cfe27c4cd375e1c999f02f186f617f6.us.langgraph.app make benchmark-burst

# Clean up result files
make benchmark-clean
```

### Output

Summary results are written to stdout and persisted in a summary_burst file. More detailed results for the same burst are persisted in a results_burst file.

Charts can be created from the run locally using the `make benchmark-charts` command.

## Resources

- [K6 Documentation](https://k6.io/docs/)
- [K6 JavaScript API](https://k6.io/docs/javascript-api/)
- [Performance Testing Best Practices](https://k6.io/docs/testing-guides/) 