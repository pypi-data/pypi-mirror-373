# ivoryOS client

## Description
[ivoryOS](https://gitlab.com/heingroup/ivoryos) client automates the generation of client-side APIs based on server-defined robotic control script. 
It mirrors the control Python code features but sending command through HTTP request to the ivoryOS backend (where the actual robotic communication are happening) that receives the info and execute the actual control methods.

## Installation
```bash
pip install ivoryos-client
```

## Quick Start

```python
from ivoryos_client import IvoryosClient

# Initialize client
client = IvoryosClient(
    url="http://localhost:8000/ivoryos",
    username="admin",
    password="admin"
)

# Or use as context manager
with IvoryosClient(url="http://localhost:8000/ivoryos", username="admin", password="admin") as client:
    # Get platform info
    info = client.get_platform_info()
    print(info)
    
    # Check execution status
    status = client.get_execution_status()
    print(status)
    
    # Execute a task
    result = client.execute_task("sdl", "dose_solid", {"amount_in_mg": "5"})
    print(result)
```

## Features

- **Task Execution**: Execute robot tasks with parameters
- **Workflow Management**: Submit, load, and manage workflow scripts
- **Workflow Execution**: Run workflows with different strategies (repeat, kwargs, campaign)
- **Data Management**: List and load workflow execution data
- **Status Monitoring**: Check workflow execution status
- **Error Handling**: Comprehensive exception handling with specific error types

## API Reference

### Client Initialization

```python
IvoryosClient(url, username, password, timeout=30.0)
```

### Task Operations

- `execute_task(component, method, kwargs=None)` - Execute a task
- `get_execution_status()` - Get current execution status

### Workflow Script Operations

- `list_workflow_scripts(search_key='', deck_name='')` - List available scripts
- `load_workflow_script(workflow_name)` - Load a specific script
- `submit_workflow_script(workflow_name, main_script='', cleanup_script='', prep_script='')` - Submit a script

### Workflow Execution

- `run_workflow_repeat(repeat_time=None)` - Run workflow with simple repeat
- `run_workflow_kwargs(kwargs_list=None)` - Run workflow with parameter sets
- `run_workflow_campaign(parameters, objectives, repeat=25, parameter_constraints=None)` - Run optimization campaign

### Workflow Control

- `pause_and_resume()` - Toggle workflow pause/resume
- `abort_pending_workflow()` - Abort pending executions
- `stop_current_workflow()` - Stop current execution

### Data Operations

- `list_workflow_data(workflow_name='')` - List workflow execution data
- `load_workflow_data(workflow_id)` - Load specific workflow data

## Exception Handling

The client provides specific exception types:

- `IvoryosError` - Base exception
- `AuthenticationError` - Authentication failures
- `ConnectionError` - Connection issues
- `WorkflowError` - Workflow operation failures
- `TaskError` - Task execution failures

```python
from ivoryos_client import IvoryosClient, AuthenticationError, WorkflowError

try:
    with IvoryosClient(url="http://localhost:8000/ivoryos", username="admin", password="admin") as client:
        result = client.execute_task("sdl", "dose_solid", {"amount_in_mg": "5"})
except AuthenticationError:
    print("Authentication failed")
except WorkflowError as e:
    print(f"Workflow error: {e}")
```

## Development

### Setup Development Environment

```bash
git clone https://gitlab.com/heingroup/ivoryos-suite/ivoryos-client
cd ivoryos-client
pip install -e ".[dev]"
```

## License

MIT License

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Run the test suite
6. Submit a pull request
