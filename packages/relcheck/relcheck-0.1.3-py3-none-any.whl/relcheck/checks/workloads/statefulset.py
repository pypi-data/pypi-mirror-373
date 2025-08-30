from __future__ import annotations

from ...core.types import ReportInfo, BaseCheck
from ...resources.workloads import StatefulSetResource


class StatefulSetPvcCheck(BaseCheck):
    id = "STS_PVC"
    title = "StatefulSet should reference a volumeClaimTemplates"
    category = "misconfig"
    target_kind = "StatefulSet"

    def run(self, resource: StatefulSetResource) -> ReportInfo:
        has_vct = bool((resource.raw.get("spec", {}) or {}).get("volumeClaimTemplates"))
        passed = has_vct
        details = "volumeClaimTemplates present" if passed else "no volumeClaimTemplates defined"
        return ReportInfo(
            resource_kind=resource.kind, 
            resource_name=resource.name, 
            namespace=resource.namespace, 
            check_id=self.id, 
            check_title=self.title, 
            category=self.category, 
            passed=passed, 
            details=details,
            description="StatefulSets need persistent storage for stateful applications. Docs: https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/#persistentvolumeclaim",
            probable_cause="StatefulSet created without volumeClaimTemplates for persistent storage"
        )


