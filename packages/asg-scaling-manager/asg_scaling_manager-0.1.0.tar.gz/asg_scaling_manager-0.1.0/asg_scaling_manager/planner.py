"""Capacity distribution planner."""

from __future__ import annotations

from typing import List, Optional

from .models import AsgInfo, CapacityUpdate, Plan


def plan_zero(asgs: List[AsgInfo]) -> Plan:
    return Plan(
        updates=[CapacityUpdate(name=a.name, desired=0, min_size=0, max_size=0) for a in asgs]
    )


def plan_equal_split(asgs: List[AsgInfo], total_desired: int, per_asg_max_cap: Optional[int]) -> Plan:
    if not asgs:
        return Plan(updates=[])
    n = len(asgs)

    # Compute caps per ASG considering existing MaxSize and optional per-ASG cap
    caps: List[int] = []
    for a in asgs:
        cap = a.max_size
        if per_asg_max_cap is not None:
            cap = min(cap, per_asg_max_cap)
        caps.append(max(0, cap))

    # Initial fair share
    base = total_desired // n
    remainder = total_desired % n
    assigned: List[int] = []
    for idx, cap in enumerate(caps):
        want = base + (1 if idx < remainder else 0)
        assigned.append(min(want, cap))

    remaining = total_desired - sum(assigned)
    if remaining > 0:
        # Top-up pass: allocate remaining to ASGs that still have headroom
        for idx, cap in enumerate(caps):
            if remaining <= 0:
                break
            headroom = cap - assigned[idx]
            if headroom <= 0:
                continue
            add = min(headroom, remaining)
            assigned[idx] += add
            remaining -= add

    updates: List[CapacityUpdate] = []
    for idx, a in enumerate(asgs):
        u = CapacityUpdate(name=a.name, desired=assigned[idx])
        if per_asg_max_cap is not None:
            u.max_size = per_asg_max_cap
        updates.append(u)

    return Plan(updates=updates)


