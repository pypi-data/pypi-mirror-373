# Novita Agent Sandbox SDK for Python

A Python SDK for Novita Agent Sandbox environments that provides code execution, desktop automation, and cloud computing capabilities. Compatible with e2b.

[📖 Documentation](https://novita.ai/docs/guides/sandbox-overview) • [🔑 Get API Key](https://novita.ai/settings/key-management) 

## Features

- **Code Interpreter**: Execute Python, JavaScript, and other languages in isolated environments
- **Desktop Automation**: Control desktop applications and GUI interactions
- **Cloud Computing**: Scalable sandbox environments for various computing tasks
- **Data Visualization**: Built-in charting and visualization capabilities
- **File System Operations**: Complete file system management and monitoring


## Installation

```bash
pip install novita-sandbox
```

## Quick Start

### Authentication

Get your Novita API key from the [key management page](https://novita.ai/settings/key-management).

### Core Sandbox

The basic package provides a way to interact with the sandbox environment.

```python
from novita_sandbox.core import Sandbox
import os

# Using the official template `base` by default
sandbox = Sandbox.create(
    template="base",
    api_key=os.getenv("NOVITA_API_KEY", "")
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
from novita_sandbox.code_interpreter import Sandbox
import os

sandbox = Sandbox.create(
    api_key=os.getenv("NOVITA_API_KEY", "")
)

# Execute Python code
result = sandbox.run_code('print("Hello, World!")')
print(result.logs)

sandbox.kill()
```

### Desktop Automation

The Desktop sandbox allows you to control desktop environments programmatically using the official `desktop` template.

```python
from novita_sandbox.desktop import Sandbox
import os

desktop = Sandbox.create(
    api_key=os.getenv("NOVITA_API_KEY", "")
)

# Take a screenshot
screenshot = desktop.screenshot()

# Automate mouse and keyboard
desktop.left_click(100, 200)
desktop.press('Return')
desktop.write('Hello, World!')

desktop.kill()
```

## Documentation

For comprehensive guides, API references, and examples, visit our [official documentation](https://novita.ai/docs/guides/sandbox-overview).
