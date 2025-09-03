# Twoly

2ly MCP client for python LangChain agents.

## Install

```bash
pip install twoly
```

## Usage

```python
from twoly import TwolyMCP
#...
tools = await TwolyMCP("Hello world").tools();
agent = create_react_agent(llm, tools)
```

# Development

## Prepare your venv

```bash
cd packages/twoly
python3.11 -m venv .venv # any version python3.10+ will do
source .venv/bin/activate
pip install --upgrade pip
pip install ".[all]"
```

## Build locally

```bash
python -m build
```

## Test local installation

```bash
pip install dist/twoly-0.1.0-py3-none-any.whl
```

## Run the examples

**List tools**

```bash
python examples/list_tools.py
```

**Agent call**

```bash
python examples/agent_call.py
```