from __future__ import annotations

from typing import Any, Dict

from ...core.types import ReportInfo, BaseCheck
from ...resources.pod import PodResource


class PodResourceLimitsCheck(BaseCheck):
    id = "POD_LIMITS"
    title = "Containers should define resource limits"
    category = "misconfig"
    target_kind = "Pod"

    def run(self, resource: PodResource) -> ReportInfo:
        missing = []
        for c in resource.containers():
            limits: Dict[str, Any] = (c.get("resources", {}) or {}).get("limits", {}) or {}
            if not limits.get("cpu") or not limits.get("memory"):
                missing.append(c.get("name", "<unnamed>"))

        passed = len(missing) == 0
        details = (
            "All containers define cpu and memory limits"
            if passed
            else f"Missing limits in containers: {', '.join(missing)}"
        )
        return ReportInfo(
            resource_kind=resource.kind,
            resource_name=resource.name,
            namespace=resource.namespace,
            check_id=self.id,
            check_title=self.title,
            category=self.category,
            passed=passed,
            details=details,
            description="Containers without cpu/memory limits can starve or evict neighbors. See Kubernetes Resource Management docs: https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/",
            probable_cause="Resources.limits missing for one or more containers",
        )


