from __future__ import annotations

from ...core.types import ReportInfo, BaseCheck
from ...resources.rbac import ClusterRoleResource


class ClusterRoleWildcardCheck(BaseCheck):
    id = "CR_WILDCARD"
    title = "ClusterRole should avoid wildcard verbs/resources"
    category = "misconfig"
    target_kind = "ClusterRole"

    def run(self, resource: ClusterRoleResource) -> ReportInfo:
        rules = resource.raw.get("rules", []) or []
        has_wildcard = any("*" in (r.get("verbs", []) or []) or "*" in (r.get("resources", []) or []) for r in rules)
        passed = not has_wildcard
        details = "no wildcards" if passed else "wildcards found in verbs/resources"
        return ReportInfo(
            resource_kind=resource.kind, 
            resource_name=resource.name, 
            namespace=None, 
            check_id=self.id, 
            check_title=self.title, 
            category=self.category, 
            passed=passed, 
            details=details,
            description="Wildcard permissions grant excessive access and violate least-privilege principle. Docs: https://kubernetes.io/docs/reference/access-authn-authz/rbac/#restrictions-on-role-creation-or-update",
            probable_cause="ClusterRole created with wildcard verbs (*) or resources (*) for convenience"
        )


