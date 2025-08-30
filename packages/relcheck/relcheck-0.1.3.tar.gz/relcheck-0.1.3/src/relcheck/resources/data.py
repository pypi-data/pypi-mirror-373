from __future__ import annotations

from typing import Any, Dict, Optional

from ..core.types import Resource
from ..core.kube import KubeContext


class ConfigMapResource(Resource):
    kind = "ConfigMap"

    @staticmethod
    def from_k8s_obj(obj: Dict[str, Any], kube_context: Optional[KubeContext] = None) -> "ConfigMapResource":
        meta = obj.get("metadata", {})
        return ConfigMapResource(name=meta.get("name", "<unknown>"), namespace=meta.get("namespace"), raw=obj, kube_context=kube_context)


class SecretResource(Resource):
    kind = "Secret"

    @staticmethod
    def from_k8s_obj(obj: Dict[str, Any], kube_context: Optional[KubeContext] = None) -> "SecretResource":
        meta = obj.get("metadata", {})
        return SecretResource(name=meta.get("name", "<unknown>"), namespace=meta.get("namespace"), raw=obj, kube_context=kube_context)


class PersistentVolumeClaimResource(Resource):
    kind = "PersistentVolumeClaim"

    @staticmethod
    def from_k8s_obj(obj: Dict[str, Any], kube_context: Optional[KubeContext] = None) -> "PersistentVolumeClaimResource":
        meta = obj.get("metadata", {})
        return PersistentVolumeClaimResource(name=meta.get("name", "<unknown>"), namespace=meta.get("namespace"), raw=obj, kube_context=kube_context)


class PersistentVolumeResource(Resource):
    kind = "PersistentVolume"

    @staticmethod
    def from_k8s_obj(obj: Dict[str, Any], kube_context: Optional[KubeContext] = None) -> "PersistentVolumeResource":
        meta = obj.get("metadata", {})
        return PersistentVolumeResource(name=meta.get("name", "<unknown>"), namespace=None, raw=obj, kube_context=kube_context)


