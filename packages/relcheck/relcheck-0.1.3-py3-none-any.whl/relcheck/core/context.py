from __future__ import annotations

from typing import Optional, Tuple, List
from dataclasses import dataclass
from kubernetes import client, config
from .kube import KubeContext


@dataclass
class ResourceTarget:
    kind: str
    name: str
    namespace: Optional[str] = None
    deep: bool = False


class ContextAnalyzer:
    """Analyzes Kubernetes context to provide smart defaults and resource detection"""
    
    def __init__(self, kube_context: KubeContext):
        self.kube = kube_context
        self._current_namespace: Optional[str] = None
        self._api_client: Optional[client.CoreV1Api] = None
        
    def get_current_namespace(self) -> str:
        """Get current namespace from kubeconfig context"""
        if self._current_namespace:
            return self._current_namespace
            
        try:
            # Try to get current namespace from kubeconfig
            contexts, active_context = config.list_kube_config_contexts()
            if active_context and 'context' in active_context:
                self._current_namespace = active_context['context'].get('namespace', 'default')
            else:
                self._current_namespace = 'default'
        except Exception:
            self._current_namespace = 'default'
            
        return self._current_namespace
    
    def detect_resource_type(self, name: str) -> Optional[Tuple[str, str]]:
        """
        Detect if name refers to a specific resource type.
        Returns (kind, namespace) if found, None if ambiguous.
        """
        try:
            api = self.kube.core_v1()
            
            # Try to find as Pod in current namespace
            try:
                pod = api.read_namespaced_pod(name=name, namespace=self.get_current_namespace())
                return ("Pod", pod.metadata.namespace)
            except:
                pass
                
            # Try to find as Namespace
            try:
                ns = api.read_namespace(name=name)
                return ("Namespace", None)
            except:
                pass
                
            # Try to find as Service in current namespace
            try:
                svc = api.read_namespaced_service(name=name, namespace=self.get_current_namespace())
                return ("Service", svc.metadata.namespace)
            except:
                pass
                
            # Try to find as Deployment in current namespace
            try:
                apps_api = self.kube.apps_v1()
                dep = apps_api.read_namespaced_deployment(name=name, namespace=self.get_current_namespace())
                return ("Deployment", dep.metadata.namespace)
            except:
                pass
                
        except Exception:
            pass
            
        return None
    
    def get_default_target(self, target: str) -> ResourceTarget:
        """
        Parse target string and return ResourceTarget with smart defaults.
        
        Examples:
        - "my-pod" → ResourceTarget("Pod", "my-pod", current_namespace)
        - "." → ResourceTarget("Namespace", current_namespace, None, deep=True)
        - "*" → ResourceTarget("Namespace", current_namespace, None, deep=True)
        - "cluster" → ResourceTarget("Cluster", "cluster", None, deep=True)
        - "all" → ResourceTarget("Cluster", "cluster", None, deep=True)
        """
        if target in [".", "*"]:
            # Check current namespace
            current_ns = self.get_current_namespace()
            return ResourceTarget("Namespace", current_ns, None, deep=True)
            
        elif target.lower() == "cluster":
            # Check entire cluster
            return ResourceTarget("Cluster", "cluster", None, deep=True)
            
        elif target.lower() == "all":
            # Check everything
            return ResourceTarget("Cluster", "cluster", None, deep=True)
            
        else:
            # Try to detect resource type
            detected = self.detect_resource_type(target)
            if detected:
                kind, namespace = detected
                return ResourceTarget(kind, target, namespace)
            else:
                # Default to current namespace if ambiguous
                current_ns = self.get_current_namespace()
                return ResourceTarget("Namespace", target, None, deep=True)
    
    def list_namespace_resources(self, namespace: str) -> List[Tuple[str, str]]:
        """List all resources in a namespace for context awareness"""
        try:
            api = self.kube.core_v1()
            resources = []
            
            # List pods
            pods = api.list_namespaced_pod(namespace)
            for pod in pods.items:
                resources.append(("Pod", pod.metadata.name))
                
            # List services
            services = api.list_namespaced_service(namespace)
            for svc in services.items:
                resources.append(("Service", svc.metadata.name))
                
            # List deployments
            apps_api = self.kube.apps_v1()
            deployments = apps_api.list_namespaced_deployment(namespace)
            for dep in deployments.items:
                resources.append(("Deployment", dep.metadata.name))
                
            return resources
            
        except Exception:
            return []
    
    def suggest_targets(self, partial: str) -> List[str]:
        """Suggest possible targets based on partial input"""
        try:
            current_ns = self.get_current_namespace()
            resources = self.list_namespace_resources(current_ns)
            
            suggestions = []
            for kind, name in resources:
                if partial.lower() in name.lower():
                    suggestions.append(f"{name} ({kind})")
                    
            return suggestions[:10]  # Limit to 10 suggestions
            
        except Exception:
            return []
