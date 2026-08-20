# MCP Learning Project — Python + pip

## Goal

Build a small MCP-based application from scratch using:

* Python
* pip
* MCP Python SDK
* SQLite
* MCP Inspector
* A local MCP client
* Eventually an LLM

No `uv`.

The project will progressively teach:

1. What MCP is
2. MCP servers
3. MCP tools
4. Tool input/output schemas
5. Resources
6. Error handling
7. Database integration
8. MCP transports
9. MCP clients
10. Connecting an LLM
11. Comparing Claude, GPT, Gemini and Llama

---

# Phase 0 — Environment

## Objective

Create an isolated Python environment and verify the MCP SDK.

## Requirements

Python 3.11+ recommended.

Create the project:

```text
mcp-learning/
```

Create a virtual environment:

```bash
python -m venv .venv
```

Windows:

```powershell
.venv\Scripts\activate
```

Linux/macOS:

```bash
source .venv/bin/activate
```

Upgrade pip:

```bash
python -m pip install --upgrade pip
```

Install MCP:

```bash
pip install "mcp[cli]"
```

Verify:

```bash
pip show mcp
```

## Test

Create:

```text
phase00_environment.py
```

with:

```python
import mcp

print("MCP imported successfully")
print(mcp.__version__)
```

Run:

```bash
python phase00_environment.py
```

Expected:

```text
MCP imported successfully
<version>
```

---

# Phase 1 — Your First MCP Server

## Objective

Understand the smallest possible MCP server.

Create:

```text
phase01_hello/
    server.py
```

Implement one tool:

```text
hello(name)
```

Example:

```text
Input:
    name = "Shachar"

Output:
    "Hello Shachar!"
```

The server should expose:

```text
hello
```

## Test

Run the server using the MCP development tooling.

The important thing to verify is that the MCP Inspector can:

1. Connect to the server
2. Discover `hello`
3. Show its input schema
4. Execute it
5. Display the result

## What you learn

```text
MCP Server
    │
    └── Tool
          │
          └── hello(name)
```

You should understand:

* `FastMCP`
* `@mcp.tool()`
* tool names
* tool descriptions
* parameters
* return values

---

# Phase 2 — Multiple Tools

## Objective

Understand how an MCP server exposes multiple capabilities.

Create:

```text
phase02_tools/
    server.py
```

Implement:

```text
add(a, b)
subtract(a, b)
multiply(a, b)
divide(a, b)
```

Example:

```text
add(10, 5)
→ 15
```

and:

```text
divide(10, 2)
→ 5
```

## Important test

Try:

```text
divide(10, 0)
```

The server must handle the error cleanly.

## What you learn

* Multiple tools
* Input validation
* Error handling
* Tool descriptions
* Why tool descriptions matter to an LLM

---

# Phase 3 — Build a Small Customer MCP

Now we stop writing toy tools.

## Objective

Create a small domain.

The server will represent a customer system.

Tools:

```text
find_customer(name)
get_customer(customer_id)
get_orders(customer_id)
get_order(order_id)
```

Example:

```text
find_customer("John")
```

returns:

```json
[
  {
    "id": 1,
    "name": "John Smith",
    "email": "john@example.com"
  }
]
```

## Project

```text
phase03_customer/
    server.py
    models.py
    data.py
```

Initially keep the data in Python.

Example:

```text
customers
orders
```

No database yet.

## Test scenarios

Test:

```text
find_customer("John")
```

Test:

```text
find_customer("DoesNotExist")
```

Test:

```text
get_customer(1)
```

Test:

```text
get_customer(9999)
```

Test:

```text
get_orders(1)
```

## What you learn

The important concept here is:

> MCP tools should represent useful business operations, not arbitrary implementation details.

For example:

Good:

```text
get_customer()
```

Bad:

```text
execute_python()
```

Good:

```text
get_orders()
```

Bad:

```text
execute_sql()
```

---

# Phase 4 — Resources

## Objective

Understand the difference between a **Tool** and a **Resource**.

Add a resource containing customer information.

For example:

```text
customers://all
```

The resource returns customer data.

Conceptually:

```text
Tool

get_customer(123)
        ↓
perform an operation
```

versus:

```text
Resource

customers://all
        ↓
provide data/context
```

## Project

```text
phase04_resources/
    server.py
    data.py
```

Expose:

```text
customers://all
```

and optionally:

```text
customers://1
customers://2
```

## Test

Use MCP Inspector to inspect the available resources.

## What you learn

Understand:

```text
Tool
    = action

Resource
    = data/context
```

This distinction becomes important when building larger MCP systems.

---

# Phase 5 — SQLite Database

## Objective

Replace the Python dictionaries with a real database.

Use:

```text
SQLite
```

No external database server is required.

Project:

```text
phase05_database/
    server.py
    database.py
    models.py
    seed.py
    app.db
```

Tables:

```text
customers
---------
id
name
email

orders
------
id
customer_id
product
amount
status
created_at
```

## Tools

Implement:

```text
find_customer(name)
get_customer(customer_id)
get_orders(customer_id)
get_order(order_id)
```

All tools now query SQLite.

## Test

Seed:

```text
10 customers
30 orders
```

Then test:

```text
find_customer("John")
```

and:

```text
get_orders(1)
```

## Important requirement

Do not expose:

```text
execute_sql(sql)
```

Instead expose controlled operations:

```text
find_customer()
get_orders()
get_order()
```

This is your first introduction to **MCP security design**.

---

# Phase 6 — Add a Mutating Tool

## Objective

Learn the difference between read-only and destructive operations.

Add:

```text
cancel_order(order_id)
```

An order can only be cancelled when:

```text
status = "PENDING"
```

It should reject:

```text
SHIPPED
DELIVERED
CANCELLED
```

## Test

Create:

```text
Order 100 → PENDING
```

Call:

```text
cancel_order(100)
```

Expected:

```text
status → CANCELLED
```

Then call it again.

Expected:

```text
error
```

## Why this matters

An LLM may decide to call tools.

Therefore your server must **never trust the model**.

The MCP server itself must enforce:

```text
authorization
validation
business rules
state transitions
```

The model is not your security boundary.

---

# Phase 7 — Add a Dangerous Operation

Add:

```text
delete_customer(customer_id)
```

But do not immediately allow it.

Require a confirmation parameter:

```text
delete_customer(
    customer_id,
    confirmation
)
```

Only allow:

```text
confirmation = "DELETE"
```

This demonstrates an important concept:

```text
LLM
 ↓
requests action
 ↓
MCP server
 ↓
validates action
 ↓
executes action
```

Never:

```text
LLM
 ↓
trusted automatically
 ↓
database
```

---

# Phase 8 — Build an MCP Client

Until now you have been using an MCP Inspector/client.

Now write your own client.

Project:

```text
phase08_client/
    client.py
```

The client should:

1. Start/connect to the MCP server
2. Initialize the MCP session
3. List available tools
4. Print their names/descriptions
5. Call a selected tool
6. Display the result

Expected output:

```text
Connected to Customer MCP

Available tools:

1. find_customer
2. get_customer
3. get_orders
4. get_order
5. cancel_order
6. delete_customer
```

Then:

```text
Calling:

get_customer(1)

Result:

{
    "id": 1,
    "name": "John Smith",
    "email": "john@example.com"
}
```

## What you learn

This is the point where the architecture becomes clear:

```text
┌─────────────────────┐
│    Your Client      │
│                     │
│    MCP Client       │
└──────────┬──────────┘
           │
           │ MCP
           ▼
┌─────────────────────┐
│    MCP Server       │
│                     │
│  Customer Tools     │
└──────────┬──────────┘
           │
           ▼
        SQLite
```

---

# Phase 9 — Add an LLM

Only now should we introduce an LLM.

The architecture becomes:

```text
User
 │
 ▼
LLM
 │
 ▼
MCP Client
 │
 ▼
MCP Server
 │
 ▼
SQLite
```

The user can ask:

```text
Find John Smith and show me his last three orders.
```

The LLM should determine that it needs:

```text
find_customer()
        ↓
get_orders()
```

The MCP server executes those operations.

The LLM then generates the final answer.

---

# Phase 10 — LLM Tool-Calling Loop

Your client will implement the basic agent loop.

Conceptually:

```text
User question
      │
      ▼
     LLM
      │
      ├── normal response
      │
      └── tool call
             │
             ▼
          MCP Client
             │
             ▼
          MCP Server
             │
             ▼
           Result
             │
             ▼
             LLM
             │
             ▼
        Final answer
```

Implement:

```text
while True:

    send conversation to LLM

    if LLM wants a tool:

        call MCP tool

        append result to conversation

    else:

        return final answer
```

This is the core of a tool-using AI agent.

---

# Phase 11 — Test Different LLMs

Now keep the MCP server completely unchanged.

Use:

```text
                 SAME MCP SERVER
                       │
       ┌───────────────┼───────────────┐
       │               │               │
      GPT            Claude         Gemini
       │               │               │
       └───────────────┼───────────────┘
                       │
                    Llama
```

Create identical test cases.

Example:

```text
Find John Smith.
Show his latest order.
```

Then:

```text
Find all orders above $500.
```

Then:

```text
Find John Smith and cancel his pending order.
```

Then:

```text
Delete John Smith.
```

The last one is particularly useful for testing whether the model understands your confirmation/security requirements.

---

# Phase 12 — Create an MCP Benchmark

Create:

```text
phase12_benchmark/
    cases.json
    runner.py
    results/
```

Example:

```json
{
  "id": "customer_001",
  "prompt": "Find John Smith and show his latest order.",
  "expected_tools": [
    "find_customer",
    "get_orders"
  ]
}
```

Create 20–50 test cases.

Measure:

```text
Tool selection
Parameter correctness
Number of tool calls
Successful completion
Invalid tool calls
Hallucinated information
Latency
Cost
```

Then compare:

```text
             GPT    Claude    Gemini    Llama
------------------------------------------------
Tool accuracy
Parameter accuracy
Task completion
Invalid calls
Latency
Cost
```

This will give you a practical understanding of the difference between the models.

---

# Phase 13 — Remote MCP Server

Until now:

```text
Client
  │
  │ local process
  ▼
MCP Server
```

Now move to:

```text
Client
  │
  │ HTTP
  ▼
MCP Server
  │
  ▼
Database
```

Learn:

* Streamable HTTP
* sessions
* authentication
* authorization
* network security
* timeouts
* logging

Project:

```text
phase13_http/
    server.py
    auth.py
    database.py
```

---

# Phase 14 — Security

Perform a dedicated security pass.

Your MCP server should protect against:

```text
1. Unauthorized tool calls
2. SQL injection
3. Path traversal
4. Arbitrary command execution
5. Excessive permissions
6. Sensitive data leakage
7. Destructive operations
8. Prompt injection through tool results
9. Malicious resource contents
10. Excessive tool invocation
```

For example, never create:

```text
execute_command(command)
```

unless there is an extremely strong security boundary around it.

Prefer:

```text
restart_service(service_name)
```

with a server-side allowlist:

```text
ALLOWED_SERVICES = {
    "customer-api",
    "order-api"
}
```

---

# Final Project Structure

At the end:

```text
mcp-learning/
│
├── phase00_environment/
│
├── phase01_hello/
│   └── server.py
│
├── phase02_tools/
│   └── server.py
│
├── phase03_customer/
│   ├── server.py
│   ├── models.py
│   └── data.py
│
├── phase04_resources/
│   └── server.py
│
├── phase05_database/
│   ├── server.py
│   ├── database.py
│   ├── models.py
│   └── seed.py
│
├── phase06_mutations/
│   └── server.py
│
├── phase07_security/
│   └── server.py
│
├── phase08_client/
│   └── client.py
│
├── phase09_llm/
│   ├── client.py
│   ├── agent.py
│   └── config.py
│
├── phase10_benchmark/
│   ├── cases.json
│   ├── runner.py
│   └── results/
│
├── phase11_http/
│   └── server.py
│
└── README.md
```

---

# Recommended Learning Order

Do not skip directly to the LLM.

Follow:

```text
Phase 0
   ↓
Python environment
   ↓
Phase 1
   ↓
First MCP server
   ↓
Phase 2
   ↓
Multiple tools
   ↓
Phase 3
   ↓
Real domain
   ↓
Phase 4
   ↓
Resources
   ↓
Phase 5
   ↓
SQLite
   ↓
Phase 6
   ↓
Mutating tools
   ↓
Phase 7
   ↓
Security
   ↓
Phase 8
   ↓
Your own MCP client
   ↓
Phase 9
   ↓
LLM
   ↓
Phase 10
   ↓
Compare models
   ↓
Phase 11
   ↓
Remote MCP
```

# Success Criteria

At the end you should be able to explain this diagram without referring to documentation:

```text
                         ┌─────────────┐
                         │    User     │
                         └──────┬──────┘
                                │
                                ▼
                         ┌─────────────┐
                         │     LLM     │
                         │             │
                         │ GPT/Claude/ │
                         │ Gemini/Llama│
                         └──────┬──────┘
                                │
                         tool decision
                                │
                                ▼
                         ┌─────────────┐
                         │ MCP Client  │
                         └──────┬──────┘
                                │
                           MCP protocol
                                │
                                ▼
                         ┌─────────────┐
                         │ MCP Server  │
                         │             │
                         │   Tools     │
                         │ Resources   │
                         │   Prompts   │
                         └──────┬──────┘
                                │
                    ┌───────────┼───────────┐
                    ▼           ▼           ▼
                 SQLite       REST        Files
```

The most important lesson is:

> **The MCP server should be independent of the LLM.**

You should be able to replace:

```text
GPT → Claude
Claude → Gemini
Gemini → Llama
```

without rewriting:

```text
Customer MCP Server
```

Only the AI/host/client layer changes.
