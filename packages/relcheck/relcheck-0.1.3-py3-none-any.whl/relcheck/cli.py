import json
from typing import Optional

import click

from .core.types import CheckRegistry, Report, NoopMcpSolver
from .resources.pod import PodResource
from .core.kube import KubeContext
from .core.context import ContextAnalyzer, ResourceTarget
from .core.discovery import register_discovered_checks
from .resources.namespace import NamespaceResource
from .resources.cluster import ClusterResource
from .core.runner import run_resource
from .checks.data.configmap import ConfigMapSizeCheck
from .checks.data.secret import SecretTypeCheck
from .checks.data.pvc import PvcStorageClassCheck
from .checks.cluster.node import NodeReadyCheck

def run_checks(target: str, format_: str, solve: bool, verbose: bool, deep: bool, kubeconfig: Optional[str], k8s_context: Optional[str]):
    """Internal function to run checks based on target"""
    # Initialize Kubernetes context
    kube_ctx = KubeContext(kubeconfig=kubeconfig, context=k8s_context)
    context_analyzer = ContextAnalyzer(kube_ctx)
    
    # Parse target with context awareness
    resource_target = context_analyzer.get_default_target(target)
    
    # Override deep flag if explicitly set
    if deep:
        resource_target.deep = True
    
    # Show what we're checking
    click.echo(f"🔍 Checking {resource_target.kind} '{resource_target.name}'", err=True)
    if resource_target.namespace:
        click.echo(f"   Namespace: {resource_target.namespace}", err=True)
    if resource_target.deep:
        click.echo(f"   Deep scan: enabled", err=True)
    
    # Initialize check registry
    registry = CheckRegistry()
    registry.register("ConfigMap", ConfigMapSizeCheck())
    registry.register("Secret", SecretTypeCheck())
    registry.register("PersistentVolumeClaim", PvcStorageClassCheck())
    registry.register("Node", NodeReadyCheck())
    register_discovered_checks(registry)
    
    # Run checks based on resource target
    report = Report()
    raw = {}
    
    if resource_target.kind.lower() == "pod":
        if not resource_target.namespace:
            raise click.UsageError(f"Pod '{resource_target.name}' requires namespace context")
        # Fetch live pod
        v1 = kube_ctx.core_v1()
        p = v1.read_namespaced_pod(name=resource_target.name, namespace=resource_target.namespace)
        raw = {
            "apiVersion": "v1",
            "kind": "Pod",
            "metadata": {"name": p.metadata.name, "namespace": p.metadata.namespace},
            "spec": {"containers": [c.to_dict() for c in (p.spec.containers or [])]},
        }
        res = PodResource.from_k8s_obj(raw, kube_context=kube_ctx)
        report.extend(run_resource(res, registry, deep=resource_target.deep))
        
    elif resource_target.kind.lower() == "namespace":
        res = NamespaceResource.from_k8s_obj({
            "apiVersion": "v1", 
            "kind": "Namespace", 
            "metadata": {"name": resource_target.name}
        }, kube_context=kube_ctx)
        report.extend(run_resource(res, registry, deep=resource_target.deep))
        
    elif resource_target.kind.lower() == "cluster":
        res = ClusterResource.from_k8s_obj({
            "kind": "Cluster", 
            "name": resource_target.name
        }, kube_context=kube_ctx)
        report.extend(run_resource(res, registry, deep=resource_target.deep))
    
    # MCP solution integration
    if solve:
        solver = NoopMcpSolver()
        report = solver.solve(report, resource_context={"resource": raw})
    
    # Output formatting
    if format_.lower() == "json":
        items = report.items if verbose else [i for i in report.items if not i.passed]
        click.echo(json.dumps([i.to_dict() for i in items], indent=2))
        return
    
    # Table output
    headers = ["KIND", "NAMESPACE", "NAME", "CHECK", "TAG", "RESULT", "DETAILS"]
    items = report.items if verbose else [i for i in report.items if not i.passed]
    rows = []
    for i in items:
        tag = i.category
        tag_colored = click.style(tag.upper(), fg="yellow") if tag == "misconfig" else click.style(tag.upper(), fg="red")
        result = click.style("PASS", fg="green") if i.passed else click.style("FAIL", fg="red")
        rows.append([
            i.resource_kind,
            i.namespace or "",
            i.resource_name,
            f"{i.check_id}: {i.check_title}",
            tag_colored,
            result,
            i.details,
        ])
    
    data = [headers] + rows
    if not rows:
        click.echo("No issues found." if not verbose else "No checks to display.")
        return
    
    col_widths = [max(len(click.unstyle(str(row[i]))) for row in data) for i in range(len(headers))]
    
    def draw_border(sep: str = "-") -> str:
        parts = [sep * (w + 2) for w in col_widths]
        return "+" + "+".join(parts) + "+"
    
    def fmt_row(row):
        cells = []
        for i, val in enumerate(row):
            text = str(val)
            pad = col_widths[i] - len(click.unstyle(text))
            cells.append(" " + text + " " + (" " * pad))
        return "|" + "|".join(cells) + "|"
    
    click.echo(draw_border("-"))
    click.echo(fmt_row(headers))
    click.echo(draw_border("="))
    for r in rows:
        click.echo(fmt_row(r))
    click.echo(draw_border("-"))

@click.command()
@click.version_option(version="0.1.3", prog_name="relcheck")
@click.argument("target", default=".")
@click.option("--format", "format_", 
              type=click.Choice(["table", "json"], case_sensitive=False), 
              default="table",
              help="Output format: table (default) or json")
@click.option("--solve", 
              is_flag=True, 
              default=False, 
              help="Enable MCP-based solution suggestions (experimental)")
@click.option("--verbose", 
              is_flag=True, 
              default=False, 
              help="Show all checks (passed and failed). Default: show only failed checks")
@click.option("--deep", 
              is_flag=True, 
              default=False, 
              help="Recursively check child resources (overrides context defaults)")
@click.option("--kubeconfig", 
              default=None, 
              help="Path to kubeconfig file (default: ~/.kube/config)")
@click.option("--context", "k8s_context", 
              default=None, 
              help="Kubernetes context to use (default: current context)")
def main(target: str, format_: str, solve: bool, verbose: bool, deep: bool, kubeconfig: Optional[str], k8s_context: Optional[str]):
    """relcheck - Kubernetes resource diagnostics and health checking tool.
    
    Run comprehensive checks against Kubernetes resources to identify common
    misconfigurations and faults. Supports live cluster inspection via kubectl
    configuration.
    
    TARGET can be:
        my-pod          # Check specific pod in current namespace
        .               # Check current namespace + all resources
        *               # Check current namespace + all resources  
        production      # Check 'production' namespace
        cluster         # Check entire cluster
        all             # Check everything (cluster + deep scan)
        
    EXAMPLES:
        # Smart defaults:
        relcheck my-pod                    # Check pod in current namespace
        relcheck .                         # Check current namespace
        relcheck production                # Check namespace
        relcheck cluster                   # Check cluster
        relcheck all                       # Check everything
        
        # With options:
        relcheck my-pod --verbose          # Show all checks
        relcheck . --format json           # JSON output
        relcheck cluster --deep            # Deep cluster scan
        
        # Traditional explicit commands:
        relcheck check-resource --resource-kind Pod --name my-pod --namespace default
    """
    run_checks(target, format_, solve, verbose, deep, kubeconfig, k8s_context)

# Keep the old command for backward compatibility
@click.group()
def legacy():
    """Legacy commands for backward compatibility"""
    pass

@legacy.command()
@click.option("--resource-kind", 
              type=click.Choice(["Pod", "Namespace", "Cluster"], case_sensitive=False), 
              required=True,
              help="Type of Kubernetes resource to check")
@click.option("--namespace", 
              default=None,
              help="Namespace containing the resource (required for Pod, optional for Namespace)")
@click.option("--name", 
              default=None,
              help="Name of the specific resource to check")
@click.option("--format", "format_", 
              type=click.Choice(["table", "json"], case_sensitive=False), 
              default="table",
              help="Output format: table (default) or json")
@click.option("--solve", 
              is_flag=True, 
              default=False, 
              help="Enable MCP-based solution suggestions (experimental)")
@click.option("--verbose", 
              is_flag=True, 
              default=False, 
              help="Show all checks (passed and failed). Default: show only failed checks")
@click.option("--deep", 
              is_flag=True, 
              default=False, 
              help="Recursively check child resources (e.g., all pods in a namespace)")
@click.option("--kubeconfig", 
              default=None, 
              help="Path to kubeconfig file (default: ~/.kube/config)")
@click.option("--context", "k8s_context", 
              default=None, 
              help="Kubernetes context to use (default: current context)")
def check_resource(resource_kind: str, namespace: Optional[str], name: Optional[str], format_: str, solve: bool, verbose: bool, deep: bool, kubeconfig: Optional[str], k8s_context: Optional[str]):
    """Run comprehensive diagnostics on Kubernetes resources (legacy command).
    
    EXAMPLES:
        # Check a specific pod
        relcheck check-resource --resource-kind Pod --name my-pod --namespace default
        
        # Check all resources in a namespace (deep scan)
        relcheck check-resource --resource-kind Namespace --name my-namespace --deep --verbose
        
        # Check entire cluster health
        relcheck check-resource --resource-kind Cluster --deep
        
        # Output as JSON for automation
        relcheck check-resource --resource-kind Pod --name my-pod --namespace default --format json
    """
    raw = {}

    registry = CheckRegistry()
    # keep a few base checks that don't need discovery (optional); then auto-discover
    registry.register("ConfigMap", ConfigMapSizeCheck())
    registry.register("Secret", SecretTypeCheck())
    registry.register("PersistentVolumeClaim", PvcStorageClassCheck())
    registry.register("Node", NodeReadyCheck())
    register_discovered_checks(registry)

    report = Report()
    kube_ctx = KubeContext(kubeconfig=kubeconfig, context=k8s_context)

    if resource_kind.lower() == "pod":
        if not name or not namespace:
            raise click.UsageError("For resource-kind Pod, --name and --namespace are required")
        # fetch live pod
        v1 = kube_ctx.core_v1()
        p = v1.read_namespaced_pod(name=name, namespace=namespace)
        raw = {
            "apiVersion": "v1",
            "kind": "Pod",
            "metadata": {"name": p.metadata.name, "namespace": p.metadata.namespace},
            "spec": {"containers": [c.to_dict() for c in (p.spec.containers or [])]},
        }
        res = PodResource.from_k8s_obj(raw, kube_context=kube_ctx)
        report.extend(run_resource(res, registry, deep=deep))
    elif resource_kind.lower() == "namespace":
        ns_name = name or namespace or "default"
        res = NamespaceResource.from_k8s_obj({"apiVersion": "v1", "kind": "Namespace", "metadata": {"name": ns_name}}, kube_context=kube_ctx)
        report.extend(run_resource(res, registry, deep=deep))
    elif resource_kind.lower() == "cluster":
        res = ClusterResource.from_k8s_obj({"kind": "Cluster", "name": name or "cluster"}, kube_context=kube_ctx)
        report.extend(run_resource(res, registry, deep=deep))

    if solve:
        solver = NoopMcpSolver()  # placeholder; replace with real MCP integration
        report = solver.solve(report, resource_context={"resource": raw})

    if format_.lower() == "json":
        items = report.items if verbose else [i for i in report.items if not i.passed]
        click.echo(json.dumps([i.to_dict() for i in items], indent=2))
        return

    # table
    # build rows (filter failures unless verbose)
    headers = ["KIND", "NAMESPACE", "NAME", "CHECK", "TAG", "RESULT", "DETAILS"]
    items = report.items if verbose else [i for i in report.items if not i.passed]
    rows = []
    for i in items:
        tag = i.category
        tag_colored = click.style(tag.upper(), fg="yellow") if tag == "misconfig" else click.style(tag.upper(), fg="red")
        result = click.style("PASS", fg="green") if i.passed else click.style("FAIL", fg="red")
        rows.append([
            i.resource_kind,
            i.namespace or "",
            i.resource_name,
            f"{i.check_id}: {i.check_title}",
            tag_colored,
            result,
            i.details,
        ])

    data = [headers] + rows
    if not rows:
        click.echo("No issues found." if not verbose else "No checks to display.")
        return

    col_widths = [max(len(click.unstyle(str(row[i]))) for row in data) for i in range(len(headers))]

    def draw_border(sep: str = "-") -> str:
        parts = [sep * (w + 2) for w in col_widths]
        return "+" + "+".join(parts) + "+"

    def fmt_row(row):
        cells = []
        for i, val in enumerate(row):
            text = str(val)
            pad = col_widths[i] - len(click.unstyle(text))
            cells.append(" " + text + " " + (" " * pad))
        return "|" + "|".join(cells) + "|"

    click.echo(draw_border("-"))
    click.echo(fmt_row(headers))
    click.echo(draw_border("="))
    for r in rows:
        click.echo(fmt_row(r))
    click.echo(draw_border("-"))
