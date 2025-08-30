from __future__ import annotations

from ...core.types import ReportInfo, BaseCheck
from ...resources.data import SecretResource


class SecretTypeCheck(BaseCheck):
    id = "SECRET_TYPE"
    title = "Secret should have a specific type (not generic Opaque)"
    category = "misconfig"
    target_kind = "Secret"

    def run(self, resource: SecretResource) -> ReportInfo:
        stype = (resource.raw.get("type") or "Opaque")
        passed = stype != "Opaque"
        details = f"type={stype}"
        return ReportInfo(
            resource_kind=resource.kind, 
            resource_name=resource.name, 
            namespace=resource.namespace, 
            check_id=self.id, 
            check_title=self.title, 
            category=self.category, 
            passed=passed, 
            details=details,
            description="Generic Opaque secrets lack type-specific validation and features. Docs: https://kubernetes.io/docs/concepts/configuration/secret/#secret-types",
            probable_cause="Secret created without specifying a specific type or using kubectl create secret generic"
        )


