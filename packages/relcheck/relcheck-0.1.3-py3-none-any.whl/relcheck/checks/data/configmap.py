from __future__ import annotations

from ...core.types import ReportInfo, BaseCheck
from ...resources.data import ConfigMapResource


class ConfigMapSizeCheck(BaseCheck):
    id = "CM_SIZE"
    title = "ConfigMap should not exceed 1Mi (common kube limit)"
    category = "misconfig"
    target_kind = "ConfigMap"

    def run(self, resource: ConfigMapResource) -> ReportInfo:
        data = resource.raw.get("data", {}) or {}
        size = sum(len(k) + len(v) for k, v in data.items())
        passed = size <= 1 * 1024 * 1024
        details = f"size={size} bytes"
        return ReportInfo(
            resource_kind=resource.kind, 
            resource_name=resource.name, 
            namespace=resource.namespace, 
            check_id=self.id, 
            check_title=self.title, 
            category=self.category, 
            passed=passed, 
            details=details,
            description="Large ConfigMaps can hit Kubernetes limits and cause pod failures. Docs: https://kubernetes.io/docs/concepts/configuration/configmap/#restrictions",
            probable_cause="ConfigMap contains large amounts of data or binary content"
        )


