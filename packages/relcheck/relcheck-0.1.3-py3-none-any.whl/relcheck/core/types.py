from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Protocol, Optional, runtime_checkable
from abc import ABC, abstractmethod


@dataclass
class ReportInfo:
    resource_kind: str
    resource_name: str
    namespace: str | None
    check_id: str
    check_title: str
    category: str  # "misconfig" | "fault"
    passed: bool
    details: str
    description: str = ""
    probable_cause: str = ""
    solution: str = ""
    extra: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Report:
    items: List[ReportInfo] = field(default_factory=list)

    def add(self, info: ReportInfo) -> None:
        self.items.append(info)

    def extend(self, infos: List[ReportInfo]) -> None:
        self.items.extend(infos)

    def to_jsonable(self) -> List[Dict[str, Any]]:
        return [i.to_dict() for i in self.items]

    def to_table(self) -> List[List[str]]:
        table: List[List[str]] = [[
            "KIND", "NAMESPACE", "NAME", "CHECK", "RESULT", "DETAILS"
        ]]
        for i in self.items:
            table.append([
                i.resource_kind,
                i.namespace or "",
                i.resource_name,
                f"{i.check_id}: {i.check_title}",
                "PASS" if i.passed else "FAIL",
                i.details,
            ])
        return table


@runtime_checkable
class Check(Protocol):
    id: str
    title: str

    def run(self, resource: "Resource") -> ReportInfo:
        ...


class BaseCheck(ABC):
    id: str
    title: str
    category: str = "misconfig"
    target_kind: str = ""  # e.g., "Pod", "Service", "Namespace", required for auto-registration

    @abstractmethod
    def run(self, resource: "Resource") -> ReportInfo:
        ...


class CheckRegistry:
    def __init__(self) -> None:
        self._by_kind: Dict[str, List[Check]] = {}

    def register(self, resource_kind: str, check: Check) -> None:
        self._by_kind.setdefault(resource_kind, []).append(check)

    def get(self, resource_kind: str) -> List[Check]:
        return list(self._by_kind.get(resource_kind, []))


class Resource:
    kind: str = "Resource"

    def __init__(self, name: str, namespace: Optional[str], raw: Dict[str, Any], kube_context: Optional["KubeContext"] = None) -> None:
        self.name = name
        self.namespace = namespace
        self.raw = raw
        self.kube_context = kube_context

    def load_checks(self, registry: CheckRegistry) -> List[Check]:
        return registry.get(self.kind)

    def run_checks(self, registry: CheckRegistry) -> List[ReportInfo]:
        results: List[ReportInfo] = []
        for check in self.load_checks(registry):
            results.append(check.run(self))
        return results

    # Hierarchy: override in subclasses to return child resources
    def children(self, registry: CheckRegistry) -> List["Resource"]:
        return []


class McpSolver(Protocol):
    def solve(self, report: Report, resource_context: Dict[str, Any] | None = None) -> Report:
        ...


class NoopMcpSolver:
    def solve(self, report: Report, resource_context: Dict[str, Any] | None = None) -> Report:
        return report


