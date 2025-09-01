# Blocks SDK

Write custom AI-enabled codebase automations in Python. Leverage a full codebase-aware API. Automatically trigger automations from Github, Slack, and other providers.

> We're currently in private alpha, we recommend consistently updating your SDK to the latest version to get the latest features and fixes.

## Getting Started

### 1. Install SDK

```bash
pip install blocks-sdk
```

### 2. Create a new Blocks project

```bash
mkdir -p .blocks/myautomation
cd .blocks/myautomation
```

### 3. Create a new automation

```python
# automation.py
from blocks import task, on

@task(name="my_automation")
@on("github.pull_request", repos=["MyOrg/MyRepo"])
def my_automation(event):
    print(event)
```

### 5. Upload your automation

```bash
blocks init --api-key <your-api-key>
blocks push automation.py
```
