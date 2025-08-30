from __future__ import annotations

from typing import Any, Dict, List, Optional

from ..core.types import Resource
from ..core.kube import KubeContext


class DeploymentResource(Resource):
    kind = "Deployment"

    @staticmethod
    def from_k8s_obj(obj: Dict[str, Any], kube_context: Optional[KubeContext] = None) -> "DeploymentResource":
        meta = obj.get("metadata", {})
        return DeploymentResource(name=meta.get("name", "<unknown>"), namespace=meta.get("namespace"), raw=obj, kube_context=kube_context)

    def containers(self) -> List[Dict[str, Any]]:
        return ((self.raw.get("spec", {}) or {}).get("template", {}).get("spec", {}) or {}).get("containers", [])
    
    @staticmethod
    def from_live(ns: str, name: str, kube_context: Optional[KubeContext]) -> "DeploymentResource":
        if kube_context is None:
            raise RuntimeError("kube_context required")
        apps = kube_context.apps_v1()
        d = apps.read_namespaced_deployment(name=name, namespace=ns)
        dd = d.to_dict()
        return DeploymentResource.from_k8s_obj(dd, kube_context=kube_context)


class StatefulSetResource(Resource):
    kind = "StatefulSet"

    @staticmethod
    def from_k8s_obj(obj: Dict[str, Any], kube_context: Optional[KubeContext] = None) -> "StatefulSetResource":
        meta = obj.get("metadata", {})
        return StatefulSetResource(name=meta.get("name", "<unknown>"), namespace=meta.get("namespace"), raw=obj, kube_context=kube_context)

    def containers(self) -> List[Dict[str, Any]]:
        return ((self.raw.get("spec", {}) or {}).get("template", {}).get("spec", {}) or {}).get("containers", [])


class DaemonSetResource(Resource):
    kind = "DaemonSet"

    @staticmethod
    def from_k8s_obj(obj: Dict[str, Any], kube_context: Optional[KubeContext] = None) -> "DaemonSetResource":
        meta = obj.get("metadata", {})
        return DaemonSetResource(name=meta.get("name", "<unknown>"), namespace=meta.get("namespace"), raw=obj, kube_context=kube_context)

    def containers(self) -> List[Dict[str, Any]]:
        return ((self.raw.get("spec", {}) or {}).get("template", {}).get("spec", {}) or {}).get("containers", [])


