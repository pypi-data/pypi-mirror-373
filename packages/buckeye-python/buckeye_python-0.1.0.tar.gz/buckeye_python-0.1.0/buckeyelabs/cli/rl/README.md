# buckeye rl Commands

This module provides reinforcement learning commands for training agents on buckeye environments using the `buckeye-vf-gym` adapter and verifiers framework.

## Configuration

API keys can be configured in two ways:

1. **Environment Variables**:
   ```bash
   export BUCKEYE_API_KEY="your-BUCKEYE_API_KEY-api-key"
   export WANDB_API_KEY="your-wandb-api-key"
   export PRIME_API_KEY="your-prime-api-key"
   ```

2. **`.env` File** (recommended):
   Create a `.env` file in your project root:
   ```env
   BUCKEYE_API_KEY=your-BUCKEYE_API_KEY-api-key
   WANDB_API_KEY=your-wandb-api-key
   PRIME_API_KEY=your-prime-api-key
   ```

BUCKEYE_API_KEY automatically loads settings from the `.env` file if present.

## Quick Start

```bash
# 1. Generate config from environment
buckeye rl init my-env:latest

# 2. Create dataset from tasks
buckeye hf tasks.json --name my-org/my-tasks

# 3. Start training (interactive mode)
buckeye rl
```

## Commands

### `buckeye rl init`

Generates a `buckeye-vf-gym` configuration file by analyzing a environment:

```bash
buckeye rl init hudpython/hud-text-2048:latest
buckeye rl init my-env:latest -o configs/my-env.yaml
buckeye rl init my-env:latest --force  # Overwrite existing
```

This command:
- Analyzes the environment's available tools
- Generates appropriate action mappings
- Creates a system prompt with tool descriptions
- Sets up default parser and rubric configurations

### `buckeye hf`

Converts tasks to HuggingFace dataset format:

```bash
buckeye hf tasks.json --name my-org/my-dataset
buckeye hf tasks.json --name my-org/private-dataset --private
buckeye hf tasks.json --name local-dataset --no-push  # Local only
```

Features:
- Validates task format
- Auto-infers MCP config from `buckeye.lock.yaml`
- Updates lock file with primary dataset reference
- Supports both single task and task array formats

### `buckeye rl` (main command)

Runs RL training with automatic setup:

```bash
# Interactive mode - prompts for missing components
buckeye rl

# Specify options
buckeye rl --model gpt-4o-mini --dataset my-org/my-tasks
buckeye rl --config configs/2048.yaml --gpus 4xH100
buckeye rl --gpus 4xH100 --provider prime
```

The command will:
1. Check for required files (config, dataset)
2. Offer to generate missing components
3. Push environment to registry if needed
4. Start training (local or remote)

## Task Format

Tasks should follow this JSON format:

```json
{
  "id": "task-001",
  "prompt": "Complete the task description",
  "mcp_config": {
    "buckeye": {
      "url": "http://localhost:8765/mcp",
      "headers": {
        "Authorization": "Bearer $buckeye_API_KEY",
        "Mcp-Image": "your-org/your-env:latest"
      }
    }
  },
  "setup_tool": {
    "name": "setup",
    "arguments": {
      "name": "function_name",
      "param": "value"
    }
  },
  "evaluate_tool": {
    "name": "evaluate",
    "arguments": {
      "name": "evaluator_name",
      "expected": "value"
    }
  },
  "metadata": {
    "difficulty": "easy",
    "category": "task_type"
  }
}
```

## Configuration Format

The generated YAML configs follow the `buckeye-vf-gym` specification:

```yaml
job:
  name: "RL Training - my-env"
  metadata:
    environment: "my-env:latest"

system_prompt: |
  You are an AI agent interacting with my-env.
  
  Available tools:
  - tool_name(params): Description
    Usage: <tool>tool_name(...)</tool>

parser:
  use_thinking: true
  xml_weight: 0.6
  action_weight: 0.4

action_mappings:
  tool_name:
    _tool: "mcp_tool_name"
    _parser:
      positional: ["param1", "param2"]
    param1:
      from_arg: "param1"

rubric:
  weights:
    task_completion: 0.8
    tool_execution: 0.1
    format_compliance: 0.1
```

## Lock File Integration

The commands integrate with `buckeye.lock.yaml`:

```yaml
image: "my-org/my-env:latest"
primary_dataset:
  name: "my-org/my-tasks"
  task_count: 50
  updated_at: "2024-01-01T00:00:00"
```

This allows:
- Automatic dataset discovery for `buckeye rl`
- MCP config inference for tasks
- Environment image tracking

## Remote Training

The `buckeye rl` command fully automates remote training on GPU instances:

1. **Automatic Pod Creation**: Provisions GPU instances via Prime Intellect API
2. **Environment Setup**: Installs all required dependencies automatically
3. **Training Execution**: Runs distributed training with vLLM inference server
4. **Live Monitoring**: Streams training logs with WANDB integration

### What Happens Automatically

When you run `buckeye rl`, the system will:

1. **Create GPU Pod**:
   - Selects lowest-cost provider (typically datacrunch)
   - Allocates specified GPUs (e.g., 2xA100 for GRPO training)
   - Configures with PyTorch CUDA image
   - Polls until SSH is available (5-20 minutes)

2. **Transfer Files**:
   - Copies your config YAML to the pod
   - Creates a custom training script

3. **Install Dependencies**:
   - Installs `uv` package manager
   - Creates Python 3.12 virtual environment
   - Installs `buckeye-vf-gym` via Prime registry
   - Installs `verifiers[train]` for GRPO training
   - Installs `flash-attn` for efficient attention

4. **Setup Training**:
   <!-- - Exports WANDB_API_KEY and BUCKEYE_API_KEY -->
   - Starts vLLM inference server on GPU 0 via tmux
   - Runs GRPO training on GPU 1
   - Logs metrics to Weights & Biases

### Required API Keys

Ensure these are set in your `.env` file or environment:
<!-- - `BUCKEYE_API_KEY`: For HUD telemetry and MCP connections -->
- `WANDB_API_KEY`: For training metrics and logging
- `PRIME_API_KEY`: For pod provisioning

### SSH Key Configuration

Before using Prime pods:
1. Generate SSH keys at: https://app.primeintellect.ai/dashboard/profile
2. Download and save as: `~/.ssh/prime_key.pem`
3. Set permissions: `chmod 400 ~/.ssh/prime_key.pem`
4. Configure Prime CLI: `prime config set-ssh-key-path ~/.ssh/prime_key.pem`
