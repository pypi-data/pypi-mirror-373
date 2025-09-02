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

# Uses default Railway API and built-in defaults (network=basecamp, etc.)
client = AcadClient()

# Start the AI pipeline with minimal inputs
job_id = client.start_pipeline_auto(
    prompt="ERC721 with minting",  # max iters/filename auto
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
    # network/owner auto-filled from defaults
    network=None,
    owner=None,
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

By default, the CLI uses built-in defaults and environment variables (if set). There are no auth prompts; set env vars if needed. The menu offers:

- AI pipeline
- Job status
- Log streaming
- Artifacts (print or save)
- ERC20 deploy
- AI helpers (generate/fix/compile)

### CLI Examples

- __Run the AI pipeline__

```bash
camp
# Choose: "Run AI → Compile → Deploy pipeline"
# Prompt: ERC721 with minting
# (network/maxIters/filename are auto)
# Wait for completion and stream logs: yes
```

- __Check status__

```bash
camp
# Choose: "Check job status"
# Job ID: <paste job id>
```

- __Stream logs__

```bash
camp
# Choose: "Stream job logs"
# Job ID: <paste job id>
# Start cursor: 0
# Follow: yes
```

- __Fetch artifacts__ (print or save to folder)

```bash
camp
# Choose: "Fetch artifacts"
# Job ID: <paste job id>
# Include: all   # or sources|abis|scripts
# Output directory (optional): ./artifacts
```

- __Deploy ERC20__ (uses default owner if not provided)

```bash
camp
# Choose: "One-click ERC20 deploy"
# Name: Camp Token
# Symbol: CAMP
# Initial supply: 1000000
# (network/owner auto)
```

- __Environment overrides__

```bash
# optional: provide auth and tweak defaults
export ACAD_API_KEY="<your-key>"
export ACAD_AUTH_HEADER="X-API-Key"
export ACAD_BASE_URL="https://acadcodegen-production.up.railway.app"
export ACAD_DEFAULT_NETWORK="basecamp"
export ACAD_DEFAULT_OWNER="0xYourWalletAddress"
export ACAD_MAX_ITERS="5"
export ACAD_DEFAULT_FILENAME="AIGenerated.sol"
camp
```

## Configuration

Environment variables:

- `ACAD_API_KEY` – API key (optional)
- `ACAD_AUTH_HEADER` – auth header name (default: `X-API-Key`)
- `ACAD_BASE_URL` – base URL (default: production Railway)
- `ACAD_DEFAULT_NETWORK` – default network (default: `basecamp`)
- `ACAD_DEFAULT_OWNER` – default owner for ERC20 (built-in default provided)
- `ACAD_MAX_ITERS` – default max iterations for pipeline (default: `5`)
- `ACAD_DEFAULT_FILENAME` – default filename for generated code (default: `AIGenerated.sol`)

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

## API Reference (Production)

- Base URL: `https://acadcodegen-production.up.railway.app`
- Auth header: `X-API-Key: <your-key>` (optional if your deployment allows anonymous)

### 1) AI Pipeline

Start the AI → Compile → Deploy pipeline

Request
```http
POST /api/ai/pipeline
Content-Type: application/json
X-API-Key: <your-key>

{
  "prompt": "ERC721 with minting",
  "network": "basecamp",
  "maxIters": 5,
  "filename": "AIGenerated.sol"
}
```

Response (job started)
```json
{
  "ok": true,
  "job": {
    "id": "ai_pipeline_<uuid>",
    "state": "running",
    "progress": 5,
    "step": "init"
  }
}
```

### 2) Job Tracking

Status
```http
GET /api/job/:id/status
```

Response (completed)
```json
{
  "ok": true,
  "data": {
    "id": "ai_pipeline_<uuid>",
    "state": "completed",
    "progress": 100,
    "step": "deploy",
    "result": {
      "network": "basecamp",
      "deployer": "0xDeployerAddress",
      "contract": "MyContract",
      "address": "0xDeployedContract",
      "params": { "args": [] },
      "explorerUrl": "https://basecamp.cloud.blockscout.com/address/0xDeployedContract"
    }
  }
}
```

Logs (stream)
```http
GET /api/job/:id/logs?since=0
```

```json
{
  "ok": true,
  "data": {
    "logs": [
      { "level": "info", "msg": "Compiled successfully" },
      { "level": "info", "msg": "Deployed at 0xDeployedContract" }
    ],
    "since": 2
  }
}
```

### 3) Artifacts

Combined
```http
GET /api/artifacts?include=all&jobId=<jobId>
```

Sources
```http
GET /api/artifacts/sources?jobId=<jobId>
```

ABIs
```http
GET /api/artifacts/abis?jobId=<jobId>
```

Scripts
```http
GET /api/artifacts/scripts?jobId=<jobId>
```

### 4) One‑Click ERC20

Request
```http
POST /api/deploy/erc20
Content-Type: application/json
X-API-Key: <your-key>

{
  "name": "Camp Token",
  "symbol": "CAMP",
  "initialSupply": "1000000",
  "owner": "0xa58DCCb0F17279abD1d0D9069Aa8711Df4a4c58E",
  "network": "basecamp"
}
```

Response
```json
{
  "ok": true,
  "result": {
    "network": "basecamp",
    "deployer": "0xDeployerAddress",
    "contract": "BusinessToken",
    "address": "0xNewTokenAddress",
    "params": {
      "name": "Camp Token",
      "symbol": "CAMP",
      "initialSupply": "1000000",
      "owner": "0xa58DCCb0F17279abD1d0D9069Aa8711Df4a4c58E"
    },
    "explorerUrl": "https://basecamp.cloud.blockscout.com/address/0xNewTokenAddress"
  }
}
```

## Testing

Here are simple ways to verify the SDK and CLI locally.

- __Install from PyPI__

```bash
python -m venv .venv && source .venv/bin/activate
python -m pip install --upgrade pip
pip install camp-codegen
```

- __SDK import smoke test__

```bash
python - <<'PY'
from acad_sdk import AcadClient
print('AcadClient OK:', bool(AcadClient))
PY
```

- __CLI help and basic navigation__

```bash
camp --help || acad --help
camp
# explore the menu; press Ctrl+C to exit
```

- __End-to-end pipeline (integration test)__

```bash
camp
# Run "AI → Compile → Deploy pipeline" with the defaults
# Confirm streaming logs and wait for completion
```

- __Artifacts retrieval__

```bash
camp
# Choose "Fetch artifacts" → Include: all → Output dir: ./artifacts
ls -la ./artifacts
```

- __ERC20 deploy__

```bash
camp
# Choose "One-click ERC20 deploy" (network/owner auto)
```

- __From source (editable)__

```bash
git clone <this repo>
cd <repo>
python -m venv .venv && source .venv/bin/activate
pip install -e .
camp
```
