![](banner.jpg)

# n8n Claude CLI

A command-line tool for managing n8n workflows programmatically via the n8n REST API with built-in git-based version control.

## Purpose

`bd` provides a simple, LLM-friendly interface to:
- List, view, create, update, and delete n8n workflows
- Export workflows to JSON files
- Track all workflow changes in git with automatic commit messages
- View workflow modification history and compare versions

## Installation

Install dependencies:

```bash
pip install -r requirements.txt
```

Configure your n8n instance credentials in the system keyring:

```bash
# Set n8n URL
python3 -c "import keyring; keyring.set_password('n8n', 'url', 'https://your-n8n-instance.com:5678')"

# Set API key
python3 -c "import keyring; keyring.set_password('n8n', 'api_key', 'YOUR_API_KEY_HERE')"
```

Verify configuration:

```bash
python3 -c "import keyring; print('URL:', keyring.get_password('n8n', 'url')); print('Key exists:', bool(keyring.get_password('n8n', 'api_key')))"
```

## Usage

### List all workflows

```bash
./bd list
```

### Get workflow details

```bash
./bd get WORKFLOW_ID
```

### Create new workflow

```bash
./bd create path/to/workflow.json
```

### Update existing workflow

```bash
# From file
./bd update WORKFLOW_ID -f path/to/workflow.json

# From stdin
cat workflow.json | ./bd update WORKFLOW_ID
```

### Delete workflow

```bash
./bd delete WORKFLOW_ID
```

### Export workflow to file

```bash
./bd export WORKFLOW_ID -o output/workflows/my_workflow.json
```

### Git version control

Commit workflow state before making changes:

```bash
./bd git-before WORKFLOW_ID "workflow_name" "Description of planned changes"
```

Commit workflow state after making changes:

```bash
./bd git-after WORKFLOW_ID "workflow_name" "Description of changes made"
```

View workflow modification history:

```bash
./bd git-history WORKFLOW_ID -n 10
```

Compare workflow versions:

```bash
./bd git-diff WORKFLOW_ID --from HEAD~2 --to HEAD
```

## Examples

### Modifying a workflow with version control

```bash
# 1. Commit current state
./bd git-before PSKLQw7n4aXBHLhi discord_assistant "Adding timeout handling"

# 2. Export for editing
./bd export PSKLQw7n4aXBHLhi -o local/workflow.json

# 3. Edit the JSON file (manually or programmatically)
# ... make changes to local/workflow.json ...

# 4. Update the workflow
./bd update PSKLQw7n4aXBHLhi -f local/workflow.json

# 5. Commit new state
./bd git-after PSKLQw7n4aXBHLhi discord_assistant "Added 30s timeout to API calls"
```

### Finding workflows by name

```bash
./bd list | grep "discord"
```

### Backing up all workflows

```bash
for id in $(./bd list | awk '{print $1}' | tr -d '[]'); do
  ./bd export $id -o local/backup_${id}.json
done
```

### Cloning a workflow

```bash
# Export existing workflow
./bd export WORKFLOW_ID -o local/template.json

# Edit the JSON to change the name and remove the id field
# ... edit local/template.json ...

# Create as new workflow
./bd create local/template.json
```

### Viewing workflow change history

```bash
# See what changed in the last 5 modifications
./bd git-history WORKFLOW_ID -n 5

# Compare current version with version from 3 commits ago
./bd git-diff WORKFLOW_ID --from HEAD~3 --to HEAD
```

## Getting Help

Get help on any command:

```bash
./bd -h
./bd list -h
./bd update -h
```