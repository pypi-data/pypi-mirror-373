from __future__ import annotations

from ...core.types import ReportInfo, BaseCheck
from ...resources.cluster import ClusterResource
from ...core.kube import KubeContext


class MetricsServerDownCheck(BaseCheck):
    id = "METRICS_SERVER_DOWN"
    title = "metrics-server not available"
    category = "fault"
    target_kind = "Cluster"

    def run(self, resource: ClusterResource) -> ReportInfo:
        kube: KubeContext | None = resource.kube_context
        down = False
        detail = ""
        try:
            if kube:
                v1 = kube.core_v1()
                pods = v1.list_namespaced_pod("kube-system", label_selector="k8s-app=metrics-server")
                if not pods.items:
                    down = True
                    detail = "no metrics-server pods"
        except Exception:
            pass
        return ReportInfo(
            resource_kind=resource.kind, 
            resource_name=resource.name, 
            namespace=None, 
            check_id=self.id, 
            check_title=self.title, 
            category=self.category, 
            passed=not down, 
            details=detail or "ok", 
            description="HPA/top require metrics-server. Docs: https://github.com/kubernetes-sigs/metrics-server", 
            probable_cause="metrics-server not deployed or failing"
        )


class KubeProxyDownCheck(BaseCheck):
    id = "KUBE_PROXY_DOWN"
    title = "kube-proxy not running on nodes"
    category = "fault"
    target_kind = "Cluster"

    def run(self, resource: ClusterResource) -> ReportInfo:
        kube: KubeContext | None = resource.kube_context
        issue = False
        detail = ""
        try:
            if kube:
                v1 = kube.core_v1()
                ds = v1.list_namespaced_pod("kube-system", label_selector="k8s-app=kube-proxy")
                if not ds.items:
                    issue = True
                    detail = "no kube-proxy pods"
        except Exception:
            pass
        return ReportInfo(
            resource_kind=resource.kind, 
            resource_name=resource.name, 
            namespace=None, 
            check_id=self.id, 
            check_title=self.title, 
            category=self.category, 
            passed=not issue, 
            details=detail or "ok", 
            description="Service routing requires kube-proxy or eBPF replacement. Docs: https://kubernetes.io/docs/concepts/cluster-administration/proxies/", 
            probable_cause="kube-proxy daemonset not scheduled or failing"
        )


