from __future__ import annotations

from typing import Any, Dict, List, Optional

from ..core.types import Resource, ReportInfo, Check, CheckRegistry
from ..core.kube import KubeContext


class PodResource(Resource):
    kind = "Pod"

    @staticmethod
    def from_k8s_obj(obj: Dict[str, Any], kube_context: Optional[KubeContext] = None) -> "PodResource":
        meta = obj.get("metadata", {})
        return PodResource(
            name=meta.get("name", "<unknown>"),
            namespace=meta.get("namespace"),
            raw=obj,
            kube_context=kube_context,
        )

    def containers(self) -> List[Dict[str, Any]]:
        return (self.raw.get("spec", {}) or {}).get("containers", [])

    def run_checks(self, registry: CheckRegistry) -> List[ReportInfo]:
        return super().run_checks(registry)


