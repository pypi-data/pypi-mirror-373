from __future__ import annotations

from ...core.types import ReportInfo, BaseCheck
from ...resources.nodes import NodeResource


class NodeCordonedCheck(BaseCheck):
    id = "NODE_CORDONED"
    title = "Node is cordoned"
    category = "fault"
    target_kind = "Node"

    def run(self, resource: NodeResource) -> ReportInfo:
        unschedulable = bool((resource.raw.get("spec", {}) or {}).get("unschedulable"))
        details = "unschedulable=true" if unschedulable else "ok"
        return ReportInfo(resource_kind=resource.kind, resource_name=resource.name, namespace=None, check_id=self.id, check_title=self.title, category=self.category, passed=not unschedulable, details=details, description="Cordoned nodes don't accept new pods. Docs: https://kubernetes.io/docs/concepts/architecture/nodes/#manual-node-administration", probable_cause="Node cordoned for maintenance or failures")


