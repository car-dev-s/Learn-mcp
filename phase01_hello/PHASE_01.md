# Phase 1 — First MCP Server

## 1. Objective

Build the smallest useful MCP server using:

* Python
* `pip`
* MCP Python SDK `1.26.0`
* MCP Inspector

The server will expose exactly one tool:

```text
hello(name)
```

Example:

```text
Input:
    name = "Shachar"

Output:
    Hello, Shachar!
```

At this stage there is **no LLM**.

The architecture is:

```text
┌─────────────────────┐
│   MCP Inspector     │
│                     │
│     MCP Client      │
└──────────┬──────────┘
           │
           │ MCP
           ▼
┌─────────────────────┐
│    MCP Server       │
│                     │
│  hello(name)        │
└─────────────────────┘
```

The purpose of this phase is to understand the MCP protocol and server before introducing an AI model.

---

# 2. Prerequisites

Phase 0 must be completed successfully.

You should already have:

```text
Python 3.11+
pip
virtual environment
mcp==1.26.0
```

Verify:

```powershell
python -m pip show mcp
```

Expected:

```text
Name: mcp
Version: 1.26.0
```

Also verify:

```powershell
python --version
```

---

# 3. Project Structure

Create the following structure:

```text
mcp-learning/
│
├── .venv/
│
├── requirements.txt
│
├── phase00_environment/
│   └── check_environment.py
│
└── phase01_hello/
    ├── server.py
    └── PHASE_01.md
```

The `.venv` directory should not be committed to Git.

---

# 4. Create the MCP Server

Create:

```text
phase01_hello/server.py
```

Use the following code:

```python
from mcp.server.fastmcp import FastMCP


mcp = FastMCP("hello-server")


@mcp.tool()
def hello(name: str) -> str:
    """Return a greeting for the supplied name."""
    return f"Hello, {name}!"


if __name__ == "__main__":
    mcp.run()
```

---

# 5. Understand the Code

## 5.1 Import FastMCP

```python
from mcp.server.fastmcp import FastMCP
```

`FastMCP` provides a convenient API for creating an MCP server.

---

## 5.2 Create the Server

```python
mcp = FastMCP("hello-server")
```

This creates the MCP server.

The name:

```text
hello-server
```

identifies the server.

It is useful to give MCP servers meaningful names because a client may eventually connect to multiple servers.

For example:

```text
customer-server
filesystem-server
weather-server
database-server
```

---

# 6. Create an MCP Tool

The most important part of this phase is:

```python
@mcp.tool()
```

This decorator exposes the Python function as an MCP tool.

Without the decorator:

```python
def hello(name: str) -> str:
```

the function is just an ordinary Python function.

With:

```python
@mcp.tool()
def hello(name: str) -> str:
```

it becomes an MCP tool.

The resulting MCP server exposes:

```text
hello
```

---

# 7. Define the Tool

The function is:

```python
def hello(name: str) -> str:
    """Return a greeting for the supplied name."""
    return f"Hello, {name}!"
```

It has:

### Tool name

```text
hello
```

### Input

```text
name
```

Type:

```text
string
```

### Output

```text
string
```

For example:

```text
hello("Shachar")
```

returns:

```text
Hello, Shachar!
```

---

# 8. Why Type Annotations Matter

Notice:

```python
name: str
```

and:

```python
-> str
```

The MCP SDK can use these annotations when constructing the tool's schema.

Conceptually, the client can discover something similar to:

```json
{
  "name": "hello",
  "description": "Return a greeting for the supplied name.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "name": {
        "type": "string"
      }
    },
    "required": [
      "name"
    ]
  }
}
```

The exact serialized representation can vary by SDK/protocol version, but conceptually the client learns:

```text
Tool:
    hello

Description:
    Return a greeting for the supplied name.

Input:
    name → string
```

This becomes extremely important when an LLM is introduced later.

---

# 9. Why the Description Matters

This:

```python
"""Return a greeting for the supplied name."""
```

is not just a comment.

The tool description is part of the information available to an MCP client/model.

Later, when we have:

```text
User
  ↓
LLM
  ↓
MCP Client
```

the LLM can use tool names and descriptions when deciding which tool to call.

For example, eventually we might have:

```text
find_customer()
get_customer()
get_orders()
cancel_order()
```

The descriptions will help the model determine which tool is appropriate.

Therefore, tool descriptions should be:

* Clear
* Specific
* Accurate
* Short enough to understand
* Explicit about important restrictions

---

# 10. Run the Server Directly

From the project root:

```powershell
python phase01_hello/server.py
```

You may see little or no output.

That is expected.

The server is waiting for an MCP client.

The architecture is:

```text
Terminal
   │
   │ starts
   ▼
MCP Server
   │
   │ waiting for client
   ▼
...
```

It is not a command-line program where you type:

```text
Shachar
```

into the terminal.

Stop it with:

```text
Ctrl+C
```

---

# 11. Test with MCP Inspector

The Inspector acts as an MCP client.

This is important because we want to test MCP independently from an LLM.

The architecture is:

```text
┌─────────────────────┐
│   MCP Inspector     │
│                     │
│     MCP Client      │
└──────────┬──────────┘
           │
           │ MCP
           ▼
┌─────────────────────┐
│    hello-server     │
│                     │
│  hello(name)        │
└─────────────────────┘
```

---

# 12. Start the Inspector

From the project root:

```powershell
python -m mcp dev phase01_hello/server.py
```

If the command is not available, check the installed CLI:

```powershell
python -m mcp --help
```

You can also try:

```powershell
mcp --help
```

The MCP CLI surface may differ between SDK releases, so always prefer the command exposed by the installed version.

---

# 13. Connect the Inspector

The Inspector should connect to:

```text
phase01_hello/server.py
```

Once connected, look for the available tools.

You should see:

```text
Tools
└── hello
```

---

# 14. Inspect the `hello` Tool

Select:

```text
hello
```

You should see information equivalent to:

```text
Name:
    hello

Description:
    Return a greeting for the supplied name.

Input:
    name: string
```

The important thing is that the client can discover the tool without reading your Python source code.

This is one of the core ideas of MCP:

```text
MCP Client
     │
     │ discover capabilities
     ▼
MCP Server
     │
     └── hello
```

---

# 15. Execute the Tool

Provide:

```json
{
  "name": "Shachar"
}
```

Execute the tool.

Expected result:

```text
Hello, Shachar!
```

---

# 16. Test Another Name

Use:

```json
{
  "name": "Alice"
}
```

Expected:

```text
Hello, Alice!
```

---

# 17. Test an Empty String

Use:

```json
{
  "name": ""
}
```

The current implementation will return:

```text
Hello, !
```

This is intentional.

We are not adding validation yet.

Validation will be introduced in a later phase.

---

# 18. Understand the Request Flow

When the Inspector invokes the tool, the conceptual flow is:

```text
Inspector
    │
    │ call hello
    │
    │ name = "Shachar"
    ▼
MCP Server
    │
    ▼
hello(name)
    │
    │ Python function executes
    ▼
"Hello, Shachar!"
    │
    ▼
MCP Server
    │
    ▼
Inspector
```

The important point is:

> The MCP server executes the function. The client does not execute the Python function itself.

---

# 19. There Is No LLM Yet

This is intentional.

Phase 1 contains:

```text
MCP Client
      │
      ▼
MCP Server
      │
      ▼
Python function
```

There is no:

```text
GPT
Claude
Gemini
Llama
```

We want to understand MCP first.

Later the architecture becomes:

```text
                 User
                   │
                   ▼
                 LLM
                   │
             tool decision
                   │
                   ▼
              MCP Client
                   │
                 MCP
                   │
                   ▼
              MCP Server
                   │
                   ▼
                 Tool
```

---

# 20. Why We Are Not Adding an LLM Yet

If we started with:

```text
LLM
 │
MCP Client
 │
MCP Server
 │
Python
```

and something failed, there would be several possible causes:

```text
LLM problem
MCP client problem
MCP protocol problem
MCP server problem
Python problem
```

Instead, we are testing each layer independently.

Phase 1:

```text
MCP Client
    ↓
MCP Server
    ↓
Python
```

Phase 9 will introduce the LLM.

---

# 21. Manual Tests

Perform all of these through the MCP Inspector.

## Test 1

Input:

```json
{
  "name": "Shachar"
}
```

Expected:

```text
Hello, Shachar!
```

## Test 2

Input:

```json
{
  "name": "Alice"
}
```

Expected:

```text
Hello, Alice!
```

## Test 3

Input:

```json
{
  "name": "John Smith"
}
```

Expected:

```text
Hello, John Smith!
```

## Test 4

Input:

```json
{
  "name": ""
}
```

Expected:

```text
Hello, !
```

---

# 22. Phase 1 Success Criteria

Do not move to Phase 2 until all of these are true:

```text
[ ] Python environment works

[ ] mcp==1.26.0 is installed

[ ] server.py starts successfully

[ ] MCP Inspector can connect

[ ] The server exposes a tool called "hello"

[ ] The tool has a "name" input

[ ] The input is identified as a string

[ ] hello("Shachar") works

[ ] hello("Alice") works

[ ] hello("John Smith") works

[ ] You understand the difference between
    an MCP server and an MCP client

[ ] You understand that no LLM is involved yet
```

---

# 23. Expected Project Structure

After completing Phase 1:

```text
mcp-learning/
│
├── .venv/
│
├── requirements.txt
│
├── phase00_environment/
│   └── check_environment.py
│
└── phase01_hello/
    ├── server.py
    └── PHASE_01.md
```

---

# 24. Phase 1 Final Code

The complete server should be:

```python
from mcp.server.fastmcp import FastMCP


mcp = FastMCP("hello-server")


@mcp.tool()
def hello(name: str) -> str:
    """Return a greeting for the supplied name."""
    return f"Hello, {name}!"


if __name__ == "__main__":
    mcp.run()
```

Do not add an LLM, database, HTTP server, or framework yet.

The purpose of Phase 1 is to keep the system small enough that you understand every component.

---

# 25. What Comes Next

Phase 2 will build on this server.

Instead of:

```text
hello(name)
```

we will create several tools:

```text
add(a, b)
subtract(a, b)
multiply(a, b)
divide(a, b)
```

Then we will deliberately introduce:

* Typed parameters
* Validation
* Exceptions
* MCP error handling
* Tool descriptions
* Edge cases
* Invalid input tests

The goal is to understand what makes a **good MCP tool**, not just how to expose a Python function.

---

# Phase 1 Completion

Phase 1 is complete when the following works:

```text
MCP Inspector
      │
      │
      ▼
hello-server
      │
      │
      ▼
hello("Shachar")
      │
      ▼
Hello, Shachar!
```

At that point you have built your first functional MCP server.
