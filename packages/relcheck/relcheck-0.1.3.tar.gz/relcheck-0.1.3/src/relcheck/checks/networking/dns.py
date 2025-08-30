from __future__ import annotations

from ...core.types import ReportInfo, BaseCheck
from ...resources.namespace import NamespaceResource
from ...core.kube import KubeContext


class CoreDnsCrashLoopCheck(BaseCheck):
    id = "DNS_COREDNS_CRASH"
    title = "CoreDNS pods are crashing"
    category = "fault"
    target_kind = "Namespace"

    def run(self, resource: NamespaceResource) -> ReportInfo:
        # Only meaningful for kube-system
        if resource.name != "kube-system":
            return ReportInfo(resource_kind=resource.kind, resource_name=resource.name, namespace=None, check_id=self.id, check_title=self.title, category=self.category, passed=True, details="not kube-system")
        kube: KubeContext | None = resource.kube_context
        crashing = False
        detail = ""
        try:
            if kube:
                v1 = kube.core_v1()
                pods = v1.list_namespaced_pod("kube-system", label_selector="k8s-app=kube-dns")
                for p in pods.items:
                    for cs in (p.status.container_statuses or []):
                        st = cs.state.waiting or cs.last_state.terminated
                        if st and getattr(st, "reason", "") in ("CrashLoopBackOff", "Error"):
                            crashing = True
                            detail = f"{p.metadata.name}:{cs.name}:{st.reason}"
                            break
        except Exception:
            pass
        return ReportInfo(resource_kind=resource.kind, resource_name=resource.name, namespace=None, check_id=self.id, check_title=self.title, category=self.category, passed=not crashing, details=detail or "ok", description="DNS failures when CoreDNS is down. Docs: https://kubernetes.io/docs/tasks/administer-cluster/dns-debugging-resolution/", probable_cause="CoreDNS pod crashloop or configmap error")


