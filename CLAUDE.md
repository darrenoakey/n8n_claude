# n8n Claude CLI

This project provides a CLI tool (`bd`) for managing n8n workflows programmatically via the n8n REST API. The tool is designed for LLM-friendly usage with clear commands and predictable output.

## Setup

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Configure n8n Instance

Both the n8n instance URL and API key must be stored in the system keyring. No credentials are hardcoded in the codebase.

**Set the n8n URL:**

```bash
python3 -c "import keyring; keyring.set_password('n8n', 'url', 'YOUR_N8N_URL_HERE')"
```

Example URL format: `https://your-instance.asuscomm.com:11133`

**Set the API key:**

```bash
python3 -c "import keyring; keyring.set_password('n8n', 'api_key', 'YOUR_API_KEY_HERE')"
```

**Verify configuration:**

```bash
python3 -c "import keyring; print('URL exists:', bool(keyring.get_password('n8n', 'url'))); print('API key exists:', bool(keyring.get_password('n8n', 'api_key')))"
```

## bd CLI Tool

The `bd` tool is the main interface for n8n workflow management. It uses Python argparse and delegates to stateless API client modules in `src/`.

### Available Commands

#### list - List all workflows

```bash
./bd list
```

**Output:** Formatted list of workflows with ID, name, and status

**Example:**
```
[1] My First Workflow (active)
[2] Data Processing Flow (inactive)
[3] Email Automation (active)
```

#### get - Get workflow details

```bash
./bd get WORKFLOW_ID
```

**Output:** Full workflow JSON with nodes, connections, and settings

**Example:**
```bash
./bd get 1
```

#### create - Create new workflow

```bash
./bd create PATH_TO_JSON
```

**Input:** JSON file containing workflow definition
**Output:** Created workflow ID

**Example:**
```bash
./bd create local/new_workflow.json
```

#### update - Update existing workflow

```bash
# From file
./bd update WORKFLOW_ID -f PATH_TO_JSON

# From stdin (useful for piping)
cat workflow.json | ./bd update WORKFLOW_ID
```

**Input:** Workflow ID and JSON data (file or stdin)
**Output:** Success message

**Example:**
```bash
./bd update 1 -f local/updated_workflow.json
```

#### delete - Delete workflow

```bash
./bd delete WORKFLOW_ID
```

**Output:** Success message

**Example:**
```bash
./bd delete 5
```

#### export - Export workflow to file

```bash
./bd export WORKFLOW_ID -o OUTPUT_PATH
```

**Output:** Workflow saved to specified file

**Example:**
```bash
./bd export 1 -o local/backup_workflow.json
```

## Workflow Modification Pattern (LLM-Optimized with Git Tracking)

All workflow modifications are tracked in git at `output/workflows/`. This provides complete history and rollback capability.

When modifying workflows, follow this pattern:

1. **Export current state and commit (before changes)**
   ```bash
   ./bd export WORKFLOW_ID -o output/workflows/workflow_name.json
   cd output && git add workflows/ && git commit -m "Pre-change: workflow description"
   ```

2. **Export to local for editing**
   ```bash
   ./bd export WORKFLOW_ID -o local/workflow.json
   ```

3. **Read and parse the workflow**
   Use Read tool to examine `local/workflow.json`

4. **Make modifications**
   Use Edit tool to modify the JSON file with required changes

5. **Prepare for update (remove read-only fields)**
   ```bash
   # Clean the workflow JSON (remove active, createdAt, etc.)
   python3 << 'EOF'
   import json
   with open('local/workflow.json', 'r') as f:
       wf = json.load(f)
   clean = {
       'name': wf['name'],
       'nodes': wf['nodes'],
       'connections': wf['connections'],
       'settings': wf.get('settings', {})
   }
   with open('local/workflow_clean.json', 'w') as f:
       json.dump(clean, f, indent=2)
   EOF
   ```

6. **Update the workflow**
   ```bash
   ./bd update WORKFLOW_ID -f local/workflow_clean.json
   ```

7. **Export updated state and commit (after changes)**
   ```bash
   ./bd export WORKFLOW_ID -o output/workflows/workflow_name.json
   cd output && git add workflows/ && git commit -m "Changed: description of what was modified"
   ```

8. **Verify the change**
   ```bash
   ./bd get WORKFLOW_ID
   ```

### Git Workflow History

View history of workflow changes:
```bash
cd output && git log --oneline workflows/workflow_name.json
```

Compare versions:
```bash
cd output && git diff HEAD~1 workflows/workflow_name.json
```

Rollback to previous version:
```bash
cd output && git checkout HEAD~1 workflows/workflow_name.json
./bd update WORKFLOW_ID -f workflows/workflow_name.json
```

## Common Operations

### Find a workflow by name

```bash
./bd list | grep "search term"
```

### Backup all workflows

```bash
for id in $(./bd list | grep -oE '^\[[0-9]+\]' | tr -d '[]'); do
  ./bd export $id -o local/backup_${id}.json
done
```

### Clone a workflow

```bash
# Export existing
./bd export 1 -o local/template.json

# Modify the name (remove 'id' field to create new)
# Use Edit tool to change name and remove id field

# Create as new workflow
./bd create local/template.json
```

## API Structure

The implementation follows DRY principles with clear separation:

- `src/n8n_client.py` - API client with stateless operations
  - `N8nConfig` - Configuration and secret management
  - `N8nClient` - Low-level HTTP request handling
  - `N8nWorkflows` - Workflow CRUD operations
  - `N8nOutput` - Formatting and display helpers

- `bd` - CLI facade using argparse
  - No business logic, only command routing
  - Color-coded output (cyan headers, green success, red errors)
  - Delegates all operations to `src/n8n_client.py`

## n8n API Endpoints

The following REST API endpoints are supported:

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/workflows` | List all workflows |
| GET | `/workflows/{id}` | Get specific workflow |
| POST | `/workflows` | Create new workflow |
| PUT | `/workflows/{id}` | Update workflow |
| DELETE | `/workflows/{id}` | Delete workflow |

**Authentication:** All requests include `X-N8N-API-KEY` header

## Error Handling

All errors include context and fail explicitly:

- Missing API key: Clear message about keyring requirement
- Network errors: URL and error details
- Invalid workflow ID: API error message
- File not found: Full file path

## Testing

Tests are in `src/n8n_client_test.py`:

```bash
pytest src/n8n_client_test.py
```

Note: Integration tests require valid API key and network access. Tests gracefully skip when credentials unavailable.

## LLM Usage Notes

When using this CLI as an LLM:

1. **Git commit before and after** - Always commit current state before changes and new state after changes
2. **Always export before modifying** - Never attempt to modify workflows in memory
3. **Use output/workflows/ for versioned files** - Tracked in git for history
4. **Use local/ for temp files** - This directory is gitignored
5. **Read exported JSON** - Use the Read tool to examine workflow structure
6. **Edit precise sections** - Use Edit tool with exact old/new strings
7. **Clean JSON before update** - Remove read-only fields (active, createdAt, etc.)
8. **Verify after changes** - Always get the workflow after updating
9. **Keep workflow IDs** - Track which ID corresponds to which workflow name

### Workflow ID to Name Mapping

- `hlVEk90tMPk0Ydxw` → futuretools_scraping.json
- `j2cswHsA24ALBGjH` → hacker_news.json
- `n7pkss4ObgeQhEL5` → my_workflow.json
- `PSKLQw7n4aXBHLhi` → discord_claude_assistant.json

## File Organization

```
.
├── bd                      # Main CLI tool (executable Python)
├── src/
│   ├── n8n_client.py      # API client implementation
│   └── n8n_client_test.py # Tests
├── output/
│   ├── .git/              # Git repository for workflow history
│   ├── workflows/         # Versioned workflow exports (git tracked)
│   │   ├── futuretools_scraping.json
│   │   ├── hacker_news.json
│   │   └── my_workflow.json
│   └── testing/           # Test logs (gitignored)
├── local/                 # Temp files, working copies (gitignored)
├── requirements.txt       # Python dependencies
├── .gitignore            # Ignore output/, local/, etc.
└── CLAUDE.md             # This file
```

**Note:** The `output/` directory has its own git repository to track all workflow changes. This is separate from any project-level git repo.