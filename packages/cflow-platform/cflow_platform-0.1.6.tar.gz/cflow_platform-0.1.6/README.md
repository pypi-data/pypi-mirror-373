# CFlow Platform (Phase 1 Wrapper)

This package provides Phase 1 wrappers to allow early consumption of CFlow APIs before the full repo split.

- Public API: `cflow_platform.public_api` (proxies to monorepo `.cerebraflow/core/mcp/core/public_api.py`)
- SDK: `cflow_platform.sdk.CFlowClient` to execute MCP tools
- CLI:
  - `cflow-install-hooks` → installs enterprise git hooks (delegates to repo script when present)
  - `cflow-verify-env` → verifies required env keys per operation via the monorepo verifier

## SDK Example

```python
import asyncio
from cflow_platform.sdk import CFlowClient

async def main():
    client = CFlowClient()
    result = await client.execute_tool("sys_test")
    print(result)

asyncio.run(main())
```

## Core API (Phase 2)

```python
from cflow_platform.core.public_api import get_stdio_server, get_direct_client_executor, safe_get_version_info
```

## CLI Examples

```bash
# Verify environment for migrations + ragkg + llm
cflow-verify-env --mode migrations --mode ragkg --mode llm --scope both

# Install enterprise git hooks (delegates to scripts/install-enhanced-git-hooks.sh)
cflow-install-hooks
```

Notes: In Phase 1, this wrapper delegates to the monorepo implementations. After the split, these entry points will target packaged CFlow modules directly.
