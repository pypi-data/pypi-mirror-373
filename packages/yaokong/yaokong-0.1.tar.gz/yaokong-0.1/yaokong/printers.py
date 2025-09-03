from asyncssh import SSHCompletedProcess
from asyncssh import ProcessError
from typing import Optional, Mapping, Tuple, Union
import json
import pandas as pd

def print_ssh_completed_process(process_result):
    """
    Prints the fields of an SSHCompletedProcess object.

    Args:
        process_result (SSHCompletedProcess): The completed process result to inspect.
    """
    # Ensure the input is of the expected type
    if not isinstance(process_result, SSHCompletedProcess):
        raise ValueError("The provided argument is not an instance of SSHCompletedProcess.")

    # Define the fields to extract and their descriptions
    fields = [
        ("env", "The environment the client requested to be set for the process", "dict or None"),
        ("command", "The command the client requested the process to execute (if any)", "str or None"),
        ("subsystem", "The subsystem the client requested the process to open (if any)", "str or None"),
        ("exit_status", "The exit status returned, or -1 if an exit signal is sent", "int"),
        ("exit_signal", "The exit signal sent (if any) in the form of a tuple containing the signal name, "
                        "a bool for whether a core dump occurred, a message associated with the signal, "
                        "and the language the message was in", "tuple or None"),
        ("returncode", "The exit status returned, or negative of the signal number when an exit signal is sent", "int"),
        ("stdout", "The output sent by the process to stdout (if not redirected)", "str or bytes"),
        ("stderr", "The output sent by the process to stderr (if not redirected)", "str or bytes"),
    ]

    # Print each field and its value
    print("Fields of SSHCompletedProcess:")
    print("--------------------------------")
    for field_name, description, field_type in fields:
        value = getattr(process_result, field_name, None)
        print(f"{field_name}: {value}")
        print(f"  Description: {description}")
        print(f"  Type: {field_type}")
        print()


def print_process_error_fields(process_error):
    """
    Prints the fields of an asyncssh.ProcessError exception.

    Args:
        process_error (asyncssh.ProcessError): The exception instance to inspect.
    """
    if not isinstance(process_error, ProcessError):
        raise ValueError("The provided argument is not an instance of asyncssh.ProcessError.")

    # Define the fields to extract and their descriptions
    fields = [
        ("env", "The environment the client requested to be set for the process"),
        ("command", "The command the client requested the process to execute (if any)"),
        ("subsystem", "The subsystem the client requested the process to open (if any)"),
        ("exit_status", "The exit status returned, or -1 if an exit signal is sent"),
        ("exit_signal", "The exit signal sent (if any) in the form of a tuple containing the signal name, "
                        "a bool for whether a core dump occurred, a message associated with the signal, "
                        "and the language the message was in"),
        ("returncode", "The exit status returned, or negative of the signal number when an exit signal is sent"),
        ("stdout", "The output sent by the process to stdout (if not redirected)"),
        ("stderr", "The output sent by the process to stderr (if not redirected)"),
        ("reason", "The reason for the error"),
        ("lang", "The language of the error message")
    ]

    # Print each field and its value
    print("Fields of asyncssh.ProcessError:")
    print("--------------------------------")
    for field_name, description in fields:
        value = getattr(process_error, field_name, None)
        print(f"{field_name}: {value}")
        print(f"  Description: {description}")
        print()

def construct_host_ops(operations, results):
    """
    Construct a list of dictionaries grouping operations and results by host.

    Args:
        operations (list): List of Operation objects.
        results (list): List of Result objects.

    Returns:
        list: A list of dictionaries in the desired format.
    """
    # Dictionary to group operations and results by host
    host_dict = {}

    # Iterate over operations and results simultaneously
    for operation, result in zip(operations, results):
        host = operation.host_info['host']  # Extract host from operation
        stdout = result.cp.stdout.strip() if result.cp.stdout else "<no stdout>"  # Extract stdout from result

        # Group by host
        if host not in host_dict:
            host_dict[host] = []
        host_dict[host].append(
            ({"command": operation.command, "condition": operation.condition, "changed": operation.changed},
             {"stdout": stdout, "returncode": result.cp.returncode, "executed": result.executed,
              "changed": result.changed}))

    # Convert the dictionary into the desired list of dictionaries format
    host_ops_list = [{"host": host, "ops": ops} for host, ops in host_dict.items()]

    return host_ops_list

async def print_json_ops(host_ops):
    pretty_output = json.dumps(host_ops, indent=4)
    # Print the formatted output
    print(pretty_output)


async def generate_change_df(host_ops):
    # Step 1: Extract commands, changed, and executed values for each host
    data = {}
    for host_data in host_ops:
        host = host_data["host"]
        data[host] = []
        for op_pair in host_data["ops"]:
            # Extract the command from the first dictionary
            command = op_pair[0]["command"]
            # Merge the changed values from both dictionaries
            changed = any(d.get("changed", False) for d in op_pair)
            # Get the executed value from the second dictionary
            executed = op_pair[1].get("executed", False)
            data[host].append((command, changed, executed))
    # Step 2: Align commands across hosts
    commands = [op[0] for op in data[next(iter(data))]]  # Use the first host's commands as reference
    df_data = {}
    # Add columns for each host: <host>_changed and <host>_executed
    for host, ops in data.items():
        df_data[(host, "changed")] = [changed for _, changed, _ in ops]
        df_data[(host, "executed")] = [executed for _, _, executed in ops]
    # Step 3: Create the DataFrame with MultiIndex columns
    df = pd.DataFrame(df_data, index=commands)
    # Rename the index to "Command"
    df.index.name = "Command"
    # Display the DataFrame
    print(df)