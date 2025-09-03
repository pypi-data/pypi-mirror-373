from yaokong.operation import Operation
from yaokong.result import Result
from asyncssh import SSHCompletedProcess
import asyncssh

def pre_order_generator(node):
    """
    Generator function to perform a step-wise pre-order traversal of the tree.
    Handles delegation explicitly to ensure proper synchronization with send().
    """
    stack = [(node, iter(node.execute()))]  # Stack to keep track of nodes and their iterators
    result = None  # Initialize result as None

    while stack:
        current_node, iterator = stack[-1]  # Get the current node and its iterator
        try:
            # Send the result of the previous operation into the iterator
            value = iterator.send(result) if result is not None else next(iterator)
            result = None  # Reset result after sending

            if isinstance(value, Operation):  # If the value is an Operation, yield it
                result = yield value  # Wait for the result to be sent back
            else:  # If the value is a node, push it onto the stack
                stack.append((value, iter(value.execute())))
        except StopIteration:
            stack.pop()  # Remove the current node from the stack if its iterator is exhausted


# Define the asynchronous function to connect to a host and run a command
async def run_command_on_host(operation):
    host_info = operation.host_info
    sudo_info = operation.sudo_info
    command = operation.command
    cp = SSHCompletedProcess()
    executed = False

    if operation.condition:
        try:
            # Connect to the host
            async with asyncssh.connect(**host_info) as conn:
                # Run the command
                # Check if the command starts with 'sudo'
                # print(f"Executing command: {command}")
                if command.startswith("sudo"):
                    if not sudo_info.get("sudo_password"):
                        raise ValueError("Command requires sudo, but no sudo password was provided.")

                    # Run the command with sudo, providing the password via stdin
                    cp = await conn.run(
                        command,
                        input=sudo_info.get("sudo_password") + "\n",
                        # Provide the sudo password followed by a newline
                        check=False  # Do not raise an exception if the command fails
                    )
                else:
                    cp = await conn.run(command, check=False)

        except (OSError, asyncssh.Error) as e:
            return f"Connection failed on host {host_info.get("host")}: {str(e)}"
        executed = True

    # print(f"Output: {cp.stdout}")
    return Result(cp=cp, host=host_info.get("host"), executed=executed)



