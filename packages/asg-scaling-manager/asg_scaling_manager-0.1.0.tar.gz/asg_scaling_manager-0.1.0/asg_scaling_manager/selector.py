"""ASG selection utilities by tag and name filters."""

from __future__ import annotations

from typing import Iterable, List, Optional

from .models import AsgInfo


def filter_asgs(
    asgs: Iterable[AsgInfo],
    *,
    tag_key: str,
    tag_value: str,
    name_contains: Optional[str] = None,
    # Note: Tags are not included in AsgInfo; we filter by tag at source.
) -> List[AsgInfo]:
    # Name filter happens here; tag filter should be applied during listing.
    result: List[AsgInfo] = []
    for asg in asgs:
        if name_contains and name_contains not in asg.name:
            continue
        result.append(asg)
    return result


