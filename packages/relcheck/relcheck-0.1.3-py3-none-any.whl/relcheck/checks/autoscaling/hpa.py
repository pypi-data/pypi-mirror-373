from __future__ import annotations

from ...core.types import ReportInfo, BaseCheck
from ...resources.namespace import NamespaceResource
from ...core.kube import KubeContext


class HpaNoMetricsCheck(BaseCheck):
    id = "HPA_NO_METRICS"
    title = "HPA present but metrics missing"
    category = "fault"
    target_kind = "HorizontalPodAutoscaler"

    def run(self, resource: NamespaceResource) -> ReportInfo:
        kube: KubeContext | None = resource.kube_context
        if not kube:
            return ReportInfo(resource_kind=resource.kind, resource_name=resource.name, namespace=None, check_id=self.id, check_title=self.title, category=self.category, passed=True, details="no kube context")
        missing = False
        detail = ""
        try:
            autos = kube.autoscaling_v2()
            hpas = autos.list_namespaced_horizontal_pod_autoscaler(resource.name)
            for h in hpas.items:
                conds = h.status.conditions or []
                for c in conds:
                    if c.type == "ScalingActive" and c.status == "False":
                        missing = True
                        detail = f"{h.metadata.name}: {c.reason}"
                        break
        except Exception:
            pass
        return ReportInfo(resource_kind=resource.kind, resource_name=resource.name, namespace=None, check_id=self.id, check_title=self.title, category=self.category, passed=not missing, details=detail or "ok", description="HPA requires metrics-server or custom metrics. Docs: https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/", probable_cause="metrics-server down or metrics not configured")


