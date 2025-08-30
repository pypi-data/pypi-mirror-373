from __future__ import annotations

from typing import Any, Dict, Optional

from ..core.types import Resource
from ..core.kube import KubeContext


class RoleResource(Resource):
    kind = "Role"

    @staticmethod
    def from_k8s_obj(obj: Dict[str, Any], kube_context: Optional[KubeContext] = None) -> "RoleResource":
        meta = obj.get("metadata", {})
        return RoleResource(name=meta.get("name", "<unknown>"), namespace=meta.get("namespace"), raw=obj, kube_context=kube_context)


class RoleBindingResource(Resource):
    kind = "RoleBinding"

    @staticmethod
    def from_k8s_obj(obj: Dict[str, Any], kube_context: Optional[KubeContext] = None) -> "RoleBindingResource":
        meta = obj.get("metadata", {})
        return RoleBindingResource(name=meta.get("name", "<unknown>"), namespace=meta.get("namespace"), raw=obj, kube_context=kube_context)


class ClusterRoleResource(Resource):
    kind = "ClusterRole"

    @staticmethod
    def from_k8s_obj(obj: Dict[str, Any], kube_context: Optional[KubeContext] = None) -> "ClusterRoleResource":
        meta = obj.get("metadata", {})
        return ClusterRoleResource(name=meta.get("name", "<unknown>"), namespace=None, raw=obj, kube_context=kube_context)


class ClusterRoleBindingResource(Resource):
    kind = "ClusterRoleBinding"

    @staticmethod
    def from_k8s_obj(obj: Dict[str, Any], kube_context: Optional[KubeContext] = None) -> "ClusterRoleBindingResource":
        meta = obj.get("metadata", {})
        return ClusterRoleBindingResource(name=meta.get("name", "<unknown>"), namespace=None, raw=obj, kube_context=kube_context)


