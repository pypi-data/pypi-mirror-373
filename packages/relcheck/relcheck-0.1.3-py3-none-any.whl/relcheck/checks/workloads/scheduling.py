from __future__ import annotations

from ...core.types import ReportInfo, BaseCheck
from ...resources.namespace import NamespaceResource
from ...core.kube import KubeContext


class UnevenSchedulingCheck(BaseCheck):
    id = "UNEVENT_SCHED"
    title = "Pods unevenly scheduled across nodes"
    category = "misconfig"
    target_kind = "Namespace"

    def run(self, resource: NamespaceResource) -> ReportInfo:
        kube: KubeContext | None = resource.kube_context
        if not kube:
            return ReportInfo(resource_kind=resource.kind, resource_name=resource.name, namespace=None, check_id=self.id, check_title=self.title, category=self.category, passed=True, details="no kube context")
        try:
            v1 = kube.core_v1()
            pods = v1.list_namespaced_pod(resource.name)
            node_count = {}
            for p in pods.items:
                node = p.spec.node_name or ""
                node_count[node] = node_count.get(node, 0) + 1
            if not node_count:
                return ReportInfo(resource_kind=resource.kind, resource_name=resource.name, namespace=None, check_id=self.id, check_title=self.title, category=self.category, passed=True, details="no pods")
            maxv = max(node_count.values())
            minv = min(node_count.values())
            skew = maxv - minv
            passed = skew <= 1
            detail = f"distribution={node_count}"
            return ReportInfo(resource_kind=resource.kind, resource_name=resource.name, namespace=None, check_id=self.id, check_title=self.title, category=self.category, passed=passed, details=detail, description="Large skew suggests missing podAntiAffinity/topologySpreadConstraints. Docs: https://kubernetes.io/docs/concepts/scheduling-eviction/topology-spread-constraints/", probable_cause="No anti-affinity or spread constraints")
        except Exception:
            return ReportInfo(resource_kind=resource.kind, resource_name=resource.name, namespace=None, check_id=self.id, check_title=self.title, category=self.category, passed=True, details="error")


