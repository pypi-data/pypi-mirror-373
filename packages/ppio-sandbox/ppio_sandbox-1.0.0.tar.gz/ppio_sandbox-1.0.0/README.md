# PPIO Sandbox SDK for Python

Python SDK for PPIO Sandbox environments, providing code execution, desktop automation, and cloud computing capabilities, which is compatible with e2b.

Please read the [documentation](https://ppio.com/docs/sandbox/overview) for more information.

## Installation

```bash
pip install ppio-sandbox
```

## Features

- 🚀 **Code Interpreter**: Execute Python, JavaScript, and other languages in isolated environments
- 🖥️ **Desktop Automation**: Control desktop applications and GUI interactions
- ☁️ **Cloud Computing**: Scalable sandbox environments for various computing tasks
- 📊 **Data Visualization**: Built-in charting and visualization capabilities
- 🔧 **File System Operations**: Complete file system management and monitoring

## Quick Start

### Authentication

You can get the PPIO API key by refer to this [documentation](https://ppio.com/docs/sandbox/get-start).

### Core

The basic package provides a way to interact with the sandbox environment.

```python
from ppio_sandbox.core import Sandbox
import os

# Using the official template `base` by default
sandbox = Sandbox.create(
    template="base",
    api_key=os.getenv("PPIO_API_KEY", "")
)

# File operations
sandbox.files.write('/tmp/test.txt', 'Hello, World!')
content = sandbox.files.read('/tmp/test.txt')

# Command execution
result = sandbox.commands.run('ls -la /tmp')
print(result.stdout)

sandbox.kill()
```

### Code Interpreter

The Code Interpreter sandbox provides a Jupyter-like environment for executing code using the official `code-interpreter-v1` template.

```python
from ppio_sandbox.code_interpreter import Sandbox
import os

sandbox = Sandbox.create(
    api_key=os.getenv("PPIO_API_KEY", "")
)

# Execute Python code
result = sandbox.run_code('print("Hello, World!")')
print(result.logs)

sandbox.kill()
```

### Desktop

The Desktop sandbox allows you to control desktop environments programmatically using the official `desktop` template.

```python
from ppio_sandbox.desktop import Sandbox
import os

desktop = Sandbox.create(
    api_key=os.getenv("PPIO_API_KEY", "")
)

# Take a screenshot
screenshot = desktop.screenshot()

# Automate mouse and keyboard
desktop.left_click(100, 200)
desktop.press('Return')
desktop.write('Hello, World!')

desktop.kill()
```
