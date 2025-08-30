# relcheck

A comprehensive CLI tool for diagnosing reliability and health issues in Kubernetes clusters. relcheck performs automated health checks against live Kubernetes resources to identify common misconfigurations, faults, and potential issues before they cause problems.

## Features

- **Live Cluster Inspection**: Connects directly to Kubernetes clusters via kubectl configuration
- **Comprehensive Resource Coverage**: Supports Pods, Deployments, Services, Namespaces, and more
- **Extensible Check Framework**: Easy to add custom checks for specific resource types
- **Smart Categorization**: Distinguishes between "misconfig" (yellow) and "fault" (red) issues
- **Deep Resource Traversal**: Recursively check parent resources and all their children
- **Multiple Output Formats**: Table view (default) or JSON for automation
- **MCP Integration Ready**: Framework for AI-powered solution suggestions

## Installation

### From PyPI (Recommended)

```bash
pip install relcheck
```

### From Source

```bash
# Clone the repository
git clone <repository-url>
cd relcheck

# Install dependencies
poetry install

# Install the CLI tool
poetry install
```

## Quick Start

```bash
# Check a specific pod
relcheck check-resource --resource-kind Pod --name my-pod --namespace default

# Check all resources in a namespace (deep scan)
relcheck check-resource --resource-kind Namespace --name my-namespace --deep --verbose

# Check entire cluster health
relcheck check-resource --resource-kind Cluster --deep

# Output as JSON for automation
relcheck check-resource --resource-kind Pod --name my-pod --namespace default --format json
```

## Usage

### Basic Commands

```bash
# Get help
relcheck --help
relcheck check-resource --help

# Check a pod
relcheck check-resource --resource-kind Pod --name my-pod --namespace default

# Check a namespace with all its resources
relcheck check-resource --resource-kind Namespace --name default --deep

# Check cluster-wide resources
relcheck check-resource --resource-kind Cluster --deep
```

### Command Options

- `--resource-kind`: Type of resource (Pod, Namespace, Cluster)
- `--namespace`: Namespace containing the resource
- `--name`: Specific resource name
- `--deep`: Recursively check child resources
- `--verbose`: Show all checks (passed and failed)
- `--format`: Output format (table or json)
- `--kubeconfig`: Path to kubeconfig file
- `--context`: Kubernetes context to use
- `--solve`: Enable MCP-based solutions (experimental)

## Resource Hierarchy

relcheck understands Kubernetes resource relationships and can traverse them:

```
Cluster
├── Namespaces
│   ├── Workloads (Pods, Deployments, StatefulSets, DaemonSets)
│   ├── Networking (Services, Ingress, NetworkPolicies)
│   ├── Data (ConfigMaps, Secrets, PVCs)
│   └── RBAC (Roles, RoleBindings)
├── Nodes
└── Cluster-scoped resources (PVs, ClusterRoles, CRDs)
```

## Check Categories

### Misconfig (Yellow)
Issues that won't prevent resources from running but may cause problems:
- Missing resource limits
- Incorrect probe configurations
- Suboptimal service types

### Fault (Red)
Critical issues that can cause resource failures:
- CrashLoopBackOff states
- Image pull failures
- Resource scheduling issues
- OOM kills

## Examples

### Check Pod Health
```bash
relcheck check-resource --resource-kind Pod --name web-app --namespace production
```

### Deep Namespace Scan
```bash
relcheck check-resource --resource-kind Namespace --name production --deep --verbose
```

### Cluster-wide Health Check
```bash
relcheck check-resource --resource-kind Cluster --deep
```

## Output Formats

### Table (Default)
Shows a formatted table with resource kind, namespace, name, check details, category, result, and details.

### JSON
Machine-readable output for automation and integration:
```json
[
  {
    "resource_kind": "Pod",
    "namespace": "default",
    "resource_name": "web-app",
    "check_id": "pod_resource_limits",
    "check_title": "Pod Resource Limits Check",
    "category": "misconfig",
    "passed": false,
    "details": "Container 'web' missing memory limits",
    "description": "Check if containers have resource limits defined",
    "probable_cause": "Resource limits not specified in pod spec"
  }
]
```

## Extending relcheck

### Adding Custom Checks

Create new check classes in the appropriate resource directory:

```python
from relcheck.core.types import BaseCheck

class MyCustomCheck(BaseCheck):
    check_id = "my_custom_check"
    check_title = "My Custom Check"
    severity = "warning"
    category = "misconfig"
    target_kind = "Pod"
    description = "Description of what this check does"
    probable_cause = "Common cause of this issue"
    
    def check(self, resource, kube_context):
        # Your check logic here
        if issue_found:
            return ReportInfo(
                resource_kind=resource.kind,
                namespace=resource.namespace,
                resource_name=resource.name,
                check_id=self.check_id,
                check_title=self.check_title,
                passed=False,
                details="Issue description",
                category=self.category,
                description=self.description,
                probable_cause=self.probable_cause
            )
        return ReportInfo(...)  # Pass case
```

### Adding New Resource Types

Extend the Resource base class for new Kubernetes resource types:

```python
from relcheck.core.types import Resource

class MyResource(Resource):
    def run_checks(self, registry):
        # Run checks specific to this resource type
        pass
    
    def children(self):
        # Return child resources if any
        pass
```

## Requirements

- Python 3.11+
- Access to a Kubernetes cluster (minikube, kind, or production)
- kubectl configured with cluster access

## Development

```bash
# Clone and setup
git clone <repository-url>
cd relcheck

# Install development dependencies
poetry install

# Run tests
poetry run pytest

# Format code
poetry run black src/
poetry run isort src/

# Build package
poetry build

# Install locally for testing
poetry install
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add your changes
4. Add tests for new functionality
5. Submit a pull request

## License

[Add your license here]

