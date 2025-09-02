# Camp Codegen

Camp Codegen is a Python SDK and colorful interactive CLI for AI‑assisted smart contract generation, compilation, and deployment.

- Default API: `https://acadcodegen-production.up.railway.app`
- Default auth header: `X-API-Key: <key>` (configurable)
- Maintained by: BlockX Internet — https://blockxint.com

## Features

- AI → Compile → Deploy pipeline (one prompt to deployed contract)
- One‑click ERC20 deployment (with default owner wallet)
- Artifacts access (sources, ABIs, scripts, combined JSON)
- Live job status and log streaming
- AI helpers: generate, fix, and compile Solidity
- Colorful, interactive CLI (Rich‑powered)

## Installation

From PyPI:
```bash
pip install camp-codegen
```

Or editable install in a repo checkout:
```bash
pip install -e .
```

## Quick Start (SDK)

```python
from acad_sdk import AcadClient

client = AcadClient()  # uses default Railway API + env overrides

# Start the AI pipeline
job_id = client.start_pipeline(
    prompt="ERC721 with minting",
    network="basecamp",
    max_iters=5,
    filename="AIGenerated.sol",
)

# Wait and stream logs until completion
final = client.wait_for_completion(job_id, stream_logs=True)
print("Final:", final)

# Fetch artifacts
sources = client.get_sources(job_id)
abis = client.get_abis(job_id)
scripts = client.get_scripts(job_id)
```

### One‑click ERC20

```python
from acad_sdk import AcadClient

client = AcadClient()
res = client.deploy_erc20(
    name="Camp Token",
    symbol="CAMP",
    initial_supply="1000000",
    network="basecamp",
)
print(res)
```

## Quick Start (CLI)

Camp Codegen provides two equivalent entry points:

```bash
camp
# or
acad
```

You’ll be prompted for Base URL (default: Railway), API Key (optional), and Auth header (default: `X-API-Key`). The menu offers:

- AI pipeline
- Job status
- Log streaming
- Artifacts (print or save)
- ERC20 deploy
- AI helpers (generate/fix/compile)

## Configuration

Environment variables:

- `ACAD_API_KEY` – API key (optional)
- `ACAD_BASE_URL` – override base URL (default: production Railway)
- `ACAD_AUTH_HEADER` – override auth header name (default: `X-API-Key`)
- `ACAD_DEFAULT_OWNER` – default owner address for ERC20 (optional; built‑in default is set)

## Error Handling

Errors are raised as `AcadError` with fields `status`, `code`, and `details`. The CLI pretty‑prints error details.

## Project Layout

- `acad_sdk/` – SDK package
  - `client.py` – `AcadClient` and `AcadError`
  - `cli.py` – Rich‑powered CLI entrypoint (also exposed as `camp` and `acad`)
- `acad_cli.py` – standalone CLI script (same UX)

## License & Attribution

MIT License.

Created by BlockX Internet — https://blockxint.com
