from __future__ import annotations

from ...core.types import ReportInfo, BaseCheck
from ...resources.networking import ServiceResource
from ...core.kube import KubeContext


class ServiceSelectorCheck(BaseCheck):
    id = "SVC_SELECTOR"
    title = "Service should define a selector"
    category = "misconfig"
    target_kind = "Service"

    def run(self, resource: ServiceResource) -> ReportInfo:
        selector = (resource.raw.get("spec", {}) or {}).get("selector")
        passed = bool(selector)
        details = "selector present" if passed else "service has no selector (headless or manual)"
        return ReportInfo(
            resource_kind=resource.kind, 
            resource_name=resource.name, 
            namespace=resource.namespace, 
            check_id=self.id, 
            check_title=self.title, 
            category=self.category, 
            passed=passed, 
            details=details, 
            description="Services usually select pods via labels. Missing selector may be intentional for headless, otherwise traffic won't route. Docs: https://kubernetes.io/docs/concepts/services-networking/service/", 
            probable_cause="spec.selector missing or mismatch with pod labels"
        )


class ServiceTargetPortMismatchCheck(BaseCheck):
    id = "SVC_PORT_MISMATCH"
    title = "Service targetPort does not match container port"
    category = "fault"
    target_kind = "Service"

    def run(self, resource: ServiceResource) -> ReportInfo:
        spec = resource.raw.get("spec", {}) or {}
        selector = spec.get("selector") or {}
        ports = spec.get("ports") or []

        if not selector or not ports:
            return ReportInfo(
                resource_kind=resource.kind, 
                resource_name=resource.name, 
                namespace=resource.namespace, 
                check_id=self.id, 
                check_title=self.title, 
                category=self.category, 
                passed=True, 
                details="no selector or ports", 
                description="Service has no selector or ports to check", 
                probable_cause="N/A - no ports or selector defined"
            )

        kube: KubeContext | None = resource.kube_context
        mismatched = False
        detail = ""
        try:
            if kube:
                v1 = kube.core_v1()
                label_selector = ",".join([f"{k}={v}" for k, v in selector.items()])
                pods = v1.list_namespaced_pod(resource.namespace or "default", label_selector=label_selector)
                container_ports = set()
                for p in pods.items:
                    for c in (p.spec.containers or []):
                        for cp in (c.ports or []):
                            if cp.container_port is not None:
                                container_ports.add(int(cp.container_port))
                for prt in ports:
                    tp = prt.get("targetPort")
                    if isinstance(tp, int) and container_ports and int(tp) not in container_ports:
                        mismatched = True
                        detail = f"targetPort {tp} not in {sorted(container_ports)}"
                        break
        except Exception:
            pass

        return ReportInfo(
            resource_kind=resource.kind, 
            resource_name=resource.name, 
            namespace=resource.namespace, 
            check_id=self.id, 
            check_title=self.title, 
            category=self.category, 
            passed=not mismatched, 
            details=detail or "ok", 
            description="Service targetPort must match one of the selected pods' containerPort values. Docs: https://kubernetes.io/docs/concepts/services-networking/service/#exposing-pods-to-the-cluster", 
            probable_cause="Service port maps to a container port that does not exist"
        )


