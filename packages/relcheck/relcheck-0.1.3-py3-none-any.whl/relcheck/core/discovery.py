from __future__ import annotations

import importlib
import pkgutil
from typing import List, Type

from .types import BaseCheck, CheckRegistry


def discover_checks(package: str = "relcheck.checks") -> List[Type[BaseCheck]]:
    found: List[Type[BaseCheck]] = []
    pkg = importlib.import_module(package)
    # Ensure subpackages are imported so walk_packages can find them
    for finder, modname, ispkg in pkgutil.walk_packages(pkg.__path__, pkg.__name__ + "."):
        if ispkg:
            # import subpackage to expose its modules
            try:
                importlib.import_module(modname)
            except Exception:
                continue
            continue
        try:
            mod = importlib.import_module(modname)
        except Exception:
            continue
        for attr in dir(mod):
            obj = getattr(mod, attr)
            try:
                if isinstance(obj, type) and issubclass(obj, BaseCheck) and obj is not BaseCheck:
                    found.append(obj)
            except Exception:
                continue
    return found


def _infer_kind_from_module(module_name: str) -> str | None:
    # Heuristics based on package path
    if ".pod." in module_name:
        return "Pod"
    if ".workloads.deployment" in module_name:
        return "Deployment"
    if ".workloads.statefulset" in module_name:
        return "StatefulSet"
    if ".workloads.daemonset" in module_name:
        return "DaemonSet"
    if ".networking.service" in module_name:
        return "Service"
    if ".networking.ingress" in module_name:
        return "Ingress"
    if ".networking.networkpolicy" in module_name:
        return "NetworkPolicy"
    if ".data.configmap" in module_name:
        return "ConfigMap"
    if ".data.secret" in module_name:
        return "Secret"
    if ".data.pvc" in module_name:
        return "PersistentVolumeClaim"
    if ".nodes." in module_name or ".cluster.node" in module_name:
        return "Node"
    if ".rbac." in module_name:
        return "Namespace"
    if ".autoscaling.hpa" in module_name or ".networking.dns" in module_name or ".workloads.scheduling" in module_name:
        return "Namespace"
    if ".cluster.components" in module_name:
        return "Cluster"
    return None


def register_discovered_checks(registry: CheckRegistry) -> None:
    for check_cls in discover_checks():
        try:
            inst: BaseCheck = check_cls()  # type: ignore[call-arg]
            target_kind = getattr(inst, "target_kind", "") or _infer_kind_from_module(check_cls.__module__)
            if target_kind:
                registry.register(target_kind, inst)  # type: ignore[arg-type]
        except Exception:
            continue


