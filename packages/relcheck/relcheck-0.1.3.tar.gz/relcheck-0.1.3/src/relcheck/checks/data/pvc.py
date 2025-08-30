from __future__ import annotations

from ...core.types import ReportInfo, BaseCheck
from ...resources.data import PersistentVolumeClaimResource


class PvcStorageClassCheck(BaseCheck):
    id = "PVC_SC"
    title = "PVC should specify a StorageClass"
    category = "misconfig"
    target_kind = "PersistentVolumeClaim"

    def run(self, resource: PersistentVolumeClaimResource) -> ReportInfo:
        sc = (resource.raw.get("spec", {}) or {}).get("storageClassName")
        passed = bool(sc)
        details = f"storageClassName={sc or 'None'}"
        return ReportInfo(
            resource_kind=resource.kind, 
            resource_name=resource.name, 
            namespace=resource.namespace, 
            check_id=self.id, 
            check_title=self.title, 
            category=self.category, 
            passed=passed, 
            details=details,
            description="StorageClass ensures consistent storage provisioning and features. Docs: https://kubernetes.io/docs/concepts/storage/storage-classes/",
            probable_cause="PVC created without specifying storageClassName or using default storage class"
        )


class PvcPendingCheck(BaseCheck):
    id = "PVC_PENDING"
    title = "PVC stuck in Pending"
    category = "fault"
    target_kind = "PersistentVolumeClaim"

    def run(self, resource: PersistentVolumeClaimResource) -> ReportInfo:
        phase = ((resource.raw.get("status", {}) or {}).get("phase") or "")
        pending = phase == "Pending"
        details = f"phase={phase}"
        return ReportInfo(
            resource_kind=resource.kind, 
            resource_name=resource.name, 
            namespace=resource.namespace, 
            check_id=self.id, 
            check_title=self.title, 
            category=self.category, 
            passed=not pending, 
            details=details, 
            description="PVC Pending often means no matching StorageClass or PV capacity. Docs: https://kubernetes.io/docs/concepts/storage/persistent-volumes/", 
            probable_cause="Invalid storageClassName or insufficient PVs"
        )


