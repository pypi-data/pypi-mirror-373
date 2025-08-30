from __future__ import annotations

from ...core.types import ReportInfo, BaseCheck
from ...resources.networking import NetworkPolicyResource
from ...core.kube import KubeContext


class NetworkPolicyDenyAllCheck(BaseCheck):
    id = "NP_BASELINE"
    title = "Namespace should have a default deny-all NetworkPolicy"
    category = "misconfig"
    target_kind = "NetworkPolicy"

    def run(self, resource: NetworkPolicyResource) -> ReportInfo:
        spec = resource.raw.get("spec", {}) or {}
        # Very simplified heuristic
        has_default_deny = (spec.get("policyTypes") and set(spec.get("policyTypes")) >= {"Ingress", "Egress"} and not spec.get("ingress") and not spec.get("egress"))
        passed = has_default_deny
        details = "default deny present (heuristic)" if passed else "network policy may be too permissive"
        return ReportInfo(
            resource_kind=resource.kind, 
            resource_name=resource.name, 
            namespace=resource.namespace, 
            check_id=self.id, 
            check_title=self.title, 
            category=self.category, 
            passed=passed, 
            details=details,
            description="Default deny NetworkPolicy provides security baseline. Docs: https://kubernetes.io/docs/concepts/services-networking/network-policies/#default-deny-all-ingress-and-all-egress-traffic",
            probable_cause="No default deny NetworkPolicy configured for the namespace"
        )


class NetworkPolicyDbBlockedCheck(BaseCheck):
    id = "NP_DB_BLOCK"
    title = "Database access blocked by NetworkPolicy"
    category = "fault"
    target_kind = "NetworkPolicy"

    def run(self, resource: NetworkPolicyResource) -> ReportInfo:
        # Heuristic: if a policy selects app pods and has no egress rule to typical DB ports, flag
        spec = resource.raw.get("spec", {}) or {}
        pod_selector = spec.get("podSelector", {})
        egress = spec.get("egress")
        blocked = False
        if pod_selector is not None and egress == []:
            blocked = True
        details = "egress empty" if blocked else "ok"
        return ReportInfo(
            resource_kind=resource.kind, 
            resource_name=resource.name, 
            namespace=resource.namespace, 
            check_id=self.id, 
            check_title=self.title, 
            category=self.category, 
            passed=not blocked, 
            details=details, 
            description="Restrictive NetworkPolicy can block DB egress. Ensure egress rules allow DB ports. Docs: https://kubernetes.io/docs/concepts/services-networking/network-policies/", 
            probable_cause="Egress rules missing for database service"
        )


