# Cyberdesk Python SDK

The official Python SDK for Cyberdesk API. This SDK provides a clean, type-safe interface for interacting with all Cyberdesk resources including machines, workflows, runs, connections, and trajectories.

## Installation

```bash
pip install cyberdesk
```

## Quick Start

The most common use case is to execute workflows that you've created in the [Cyberdesk Dashboard](https://cyberdesk.io/dashboard).

```python
from cyberdesk import CyberdeskClient, RunCreate
import time

# Initialize the client
client = CyberdeskClient(api_key="your-api-key")

# Create a run for your workflow
run_data = RunCreate(
    workflow_id="your-workflow-id",
    machine_id="your-machine-id",
    input_values={
        # Your workflow-specific input data
        "patient_id": "12345",
        "patient_first_name": "John",
        "patient_last_name": "Doe"
    }
)

response = client.runs.create_sync(run_data)
if response.error:
    print(f"Error creating run: {response.error}")
else:
    run = response.data
    
    # Wait for the run to complete
    while run.status in ["scheduling", "running"]:
        time.sleep(5)  # Wait 5 seconds
        response = client.runs.get_sync(run.id)
        run = response.data
    
    # Get the output data
    if run.status == "success":
        print("Result:", run.output_data)
    else:
        print("Run failed:", ", ".join(run.error or []))
```

## Full Documentation

For complete documentation including async/sync usage, error handling, and all available methods, visit:

**[https://docs.cyberdesk.io/sdk-guides/python](https://docs.cyberdesk.io/sdk-guides/python)**

## Async Support

The SDK provides both synchronous and asynchronous methods for all operations:

```python
import asyncio
from cyberdesk import CyberdeskClient

async def main():
    client = CyberdeskClient(api_key="your-api-key")
    
    # Async method
    response = await client.machines.list()
    if response.data:
        for machine in response.data.items:
            print(f"Machine: {machine.name}")

asyncio.run(main())
```

## Resources

### Machines

```python
# List machines
response = client.machines.list_sync(
    skip=0,
    limit=10,
    status=MachineStatus.ACTIVE
)

# Get a specific machine
response = client.machines.get_sync("machine-id")

# Create a machine
from cyberdesk import MachineCreate

machine = MachineCreate(
    name="My Machine",
    provider="azure",
    region="eastus"
)
response = client.machines.create_sync(machine)

# Update a machine
from cyberdesk import MachineUpdate

update = MachineUpdate(name="Updated Name")
response = client.machines.update_sync("machine-id", update)

# Delete a machine
response = client.machines.delete_sync("machine-id")
```

### Workflows

```python
# List workflows
response = client.workflows.list_sync()

# Get a workflow
response = client.workflows.get_sync("workflow-id")

# Create a workflow
from cyberdesk import WorkflowCreate

workflow = WorkflowCreate(
    name="My Workflow",
    description="Description"
)
response = client.workflows.create_sync(workflow)

# Update a workflow
from cyberdesk import WorkflowUpdate

update = WorkflowUpdate(description="New description")
response = client.workflows.update_sync("workflow-id", update)

# Delete a workflow
response = client.workflows.delete_sync("workflow-id")
```

### Runs

```python
# List runs with filtering
response = client.runs.list_sync(
    workflow_id="workflow-id",
    machine_id="machine-id",
    status=RunStatus.RUNNING
)

# Create a run
from cyberdesk import RunCreate

run = RunCreate(
    workflow_id="workflow-id",
    machine_id="machine-id"
)
response = client.runs.create_sync(run)

# Get run details
response = client.runs.get_sync("run-id")

# Update run status
from cyberdesk import RunUpdate

update = RunUpdate(status=RunStatus.COMPLETED)
response = client.runs.update_sync("run-id", update)
```

### Connections

```python
# List connections
response = client.connections.list_sync(
    machine_id="machine-id",
    status=ConnectionStatus.ACTIVE
)

# Create a connection
from cyberdesk import ConnectionCreate

connection = ConnectionCreate(
    machine_id="machine-id",
    connection_type="vnc"
)
response = client.connections.create_sync(connection)
```

### Trajectories

```python
# List trajectories
response = client.trajectories.list_sync(workflow_id="workflow-id")

# Create a trajectory
from cyberdesk import TrajectoryCreate

trajectory = TrajectoryCreate(
    workflow_id="workflow-id",
    trajectory_data=[{"action": "click", "x": 100, "y": 200}]
)
response = client.trajectories.create_sync(trajectory)

# Get latest trajectory for a workflow
response = client.trajectories.get_latest_for_workflow_sync("workflow-id")

# Update a trajectory
from cyberdesk import TrajectoryUpdate

update = TrajectoryUpdate(
    trajectory_data=[{"action": "type", "text": "Hello"}]
)
response = client.trajectories.update_sync("trajectory-id", update)
```

## Error Handling

All methods return an `ApiResponse` object with `data` and `error` attributes:

```python
response = client.machines.get_sync("invalid-id")
if response.error:
    print(f"Error: {response.error}")
else:
    print(f"Machine: {response.data.name}")
```

## Context Manager

The client can be used as a context manager:

```python
with CyberdeskClient(api_key="your-api-key") as client:
    response = client.machines.list_sync()
    # Client will be properly closed when exiting the context
```

## Configuration

You can specify a custom API base URL:

```python
client = CyberdeskClient(
    api_key="your-api-key",
    base_url="https://custom-api.cyberdesk.io"
)
```

## Type Safety

The SDK is fully typed and exports all request/response models:

```python
from cyberdesk import (
    MachineCreate,
    MachineUpdate,
    MachineResponse,
    MachineStatus,
    WorkflowCreate,
    WorkflowResponse,
    RunCreate,
    RunStatus,
    # ... and more
)
```

## Limitations

- **Screenshot API**: The `/v1/computer/{machine_id}/display/screenshot` endpoint is not included in the generated client due to limitations with binary (PNG) responses in the openapi-python-client generator. This can be added manually if needed - see the TODO comment in `client.py`.

## Requirements

- Python 3.8+
- httpx
- pydantic

## License

MIT License - see LICENSE file for details. 