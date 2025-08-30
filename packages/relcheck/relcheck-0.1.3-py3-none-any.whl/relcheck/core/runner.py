from __future__ import annotations

from typing import List

from .types import CheckRegistry, ReportInfo, Resource


def run_resource(resource: Resource, registry: CheckRegistry, deep: bool = False) -> List[ReportInfo]:
    results: List[ReportInfo] = []
    results.extend(resource.run_checks(registry))
    if not deep:
        return results

    for child in resource.children(registry):
        results.extend(run_resource(child, registry, deep=True))
    return results


