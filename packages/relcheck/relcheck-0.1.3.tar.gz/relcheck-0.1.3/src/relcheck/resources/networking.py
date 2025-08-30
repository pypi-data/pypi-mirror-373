from __future__ import annotations

from typing import Any, Dict, Optional

from ..core.types import Resource
from ..core.kube import KubeContext


class ServiceResource(Resource):
    kind = "Service"

    @staticmethod
    def from_k8s_obj(obj: Dict[str, Any], kube_context: Optional[KubeContext] = None) -> "ServiceResource":
        meta = obj.get("metadata", {})
        return ServiceResource(name=meta.get("name", "<unknown>"), namespace=meta.get("namespace"), raw=obj, kube_context=kube_context)


class IngressResource(Resource):
    kind = "Ingress"

    @staticmethod
    def from_k8s_obj(obj: Dict[str, Any], kube_context: Optional[KubeContext] = None) -> "IngressResource":
        meta = obj.get("metadata", {})
        return IngressResource(name=meta.get("name", "<unknown>"), namespace=meta.get("namespace"), raw=obj, kube_context=kube_context)


class NetworkPolicyResource(Resource):
    kind = "NetworkPolicy"

    @staticmethod
    def from_k8s_obj(obj: Dict[str, Any], kube_context: Optional[KubeContext] = None) -> "NetworkPolicyResource":
        meta = obj.get("metadata", {})
        return NetworkPolicyResource(name=meta.get("name", "<unknown>"), namespace=meta.get("namespace"), raw=obj, kube_context=kube_context)


