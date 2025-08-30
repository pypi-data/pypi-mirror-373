from __future__ import annotations

from typing import Any, Dict, Optional

from ..core.types import Resource
from ..core.kube import KubeContext


class NodeResource(Resource):
    kind = "Node"

    @staticmethod
    def from_k8s_obj(obj: Dict[str, Any], kube_context: Optional[KubeContext] = None) -> "NodeResource":
        meta = obj.get("metadata", {})
        return NodeResource(name=meta.get("name", "<unknown>"), namespace=None, raw=obj, kube_context=kube_context)


