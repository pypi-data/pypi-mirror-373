# Yao Kong Remote Control

Yao Kong runs commands on your servers.  Yao Kong has a Python API.  It is:
- Agentless
- Declarative
- Idempotent
- Composable

# Introduction

# Motivation

Idempotency is a key feature of Yao Kong that ensures running the same task multiple times produces the same result without unintended side effects. This is particularly useful in configuration management, where tasks are often repeated to ensure consistency.

Consider creating a directory.  

```bash
mkdir /opt/myapp
```

The first time this command runs, it creates the /opt/myapp directory successfully. On subsequent runs, the command fails with an error.

One solution is to use Ansible.

```yaml
- name: Ensure /opt/myapp directory exists
  file:
    path: /opt/myapp
    state: directory
```

Ansible checks whether the /opt/myapp directory exists.  If it does, Ansible does nothing and reports the task as "ok.".  If the directory does not exist, Ansible creates it and reports the task as "changed."  

Another solution is [Pyinfra](https://pyinfra.com/).  Pyinfra pyinfra turns Python code into shell commands and runs them on your servers.  Its a great project and Yao Kong takes its inspiration from it. 

```python
files.directory(
    name="Ensure /opt/myapp directory exists",
    path="/opt/myapp",
    present=True,
)
```

Both Ansible and Pyinfra are Domain Specific Languages.  Yao Kong is a programming API that  enables you to develop your own delarative and idempotent functions.     

```python
from typing import Generator
from asyncssh import SSHCompletedProcess

# Define the directory coroutine function
def directory(path: str, present: bool) -> Generator[str, SSHCompletedProcess, None]:
    cp: SSHCompletedProcess = yield f"[ -d {path} ]"  # Check whether the directory exists
    if present and cp.returncode != 0:  # Present directory does not exist
        yield f"mkdir -p {path}"  # Create the directory
    if not present and cp.returncode == 0:  # Not Present directory exists
        yield f"rm -rf {path}"  # Remove the directory
        
yk.operation(directory(path="/opt/myapp",present=True))
```

Yao Kong creates the directory if necessary.  Unlike Ansible and Pyinfra, Yao Kong does not give an indication of whether the task changed anything.  

# Installation

See Development

# Inventory

Create a file with a function `inventory()` that returns a list hosts and their parameters.  Each host is represented by a tuple of two dictionaries.  The first dictionary contains parameters that are passed directly to [asyncssh connect](https://asyncssh.readthedocs.io/en/latest/api.html#main-functions) to connect the host.  The second dictionary contains parameters to use when sending commands to the host. 

```
from typing import List, Tuple, Dict, Any

def inventory() -> List[Tuple[Dict[str, Any], Dict[str, str]]]:
    return [
        (
            {
                'host': '192.168.122.8',         # Remote host IP address
                'username': 'alice',             # User name
                'password': 'wonderland'         # Password 
            },
            {
                'sudo_user': 'bob',              # User for sudo
                'sudo_password': 'builder'       # Password
            }
        ),
        (
            {
                'host': '192.168.122.7',         # Another remote host IP address
                'username': 'zihao',             # Another user
                'client_keys': ['/home/zihao/.ssh/id_ed25519'],  # Path to the private SSH key
                'passphrase': 'sheng'            # Password for the SSH key
            },{}
        )
    ]
```

# Development

```
# Create a virtualenv with your tool of choice
# python -m venv / pyenv virtualenv / virtualenv

# Clone the repo
git clone git@github.com:kimjarvis/yaokong.git

# Install the requirements
cd yaokong
pip install -r requirements.txt

# Install the package in editable mode 
pip install -e '.[dev]'
```

Avoid committing inventory into git.

```
# Create a directory named "inventory" to hold inventory
mkdir inventory
```
