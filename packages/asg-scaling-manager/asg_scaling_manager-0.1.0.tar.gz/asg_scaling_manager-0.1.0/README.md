# ASG Scaling Manager

Manage AWS Auto Scaling Group capacities by tag filters with a simple, reliable CLI.

## Quick Install

```bash
pip install asg-scaling-manager
```

## Usage

```bash
# Get help
asg-sm --help

# Scale ASGs tagged with eks:cluster-name=my-cluster to 6 instances total
asg-sm --tag-value my-cluster --desired 6 --dry-run

# Apply changes with optional per-ASG max cap
asg-sm --tag-value my-cluster --desired 8 --max-size 5 --region eu-west-1

# Scale down to zero (sets min/max/desired to 0)
asg-sm --tag-value my-cluster --desired 0
```

## Features

- **Tag-based filtering**: Target ASGs by `eks:cluster-name` (default) or custom tags
- **Smart distribution**: Evenly distributes desired capacity across matched ASGs
- **Safety first**: Dry-run mode to preview changes
- **EKS optimized**: Defaults to `eks:cluster-name` tag for easy EKS cluster management
- **Flexible caps**: Optional per-ASG max size limits

## Examples

```bash
# Preview scaling for production cluster
asg-sm --tag-value prod-cluster --desired 12 --dry-run

# Scale with name filter and custom tag
asg-sm --tag-key team --tag-value payments --name-contains web --desired 4

# Emergency scale down
asg-sm --tag-value staging --desired 0
```

## Notes

- **Default tag**: Uses `eks:cluster-name` by default (perfect for EKS clusters)
- **Desired vs max-size**: `--desired` is total across all ASGs, `--max-size` is per-ASG cap
- **AWS auth**: Uses `--profile` and/or `--region` for AWS credentials
- **Dry-run**: Always test with `--dry-run` first

## Alternative Installation

```bash
# Isolated install (recommended for CLIs)
pipx install asg-scaling-manager

# Development install
git clone https://github.com/grzes-94/asg-scaling-manage
cd asg-scaling-manage
pip install -e .
```
