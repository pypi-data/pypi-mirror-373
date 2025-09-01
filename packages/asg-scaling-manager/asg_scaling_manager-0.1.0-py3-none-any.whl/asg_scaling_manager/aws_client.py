"""AWS client wrapper for Auto Scaling Group operations."""

from __future__ import annotations

from typing import Iterable, List, Optional

import boto3
from botocore.config import Config

from .logging import get_logger
from .models import AsgInfo, CapacityUpdate


def create_session(profile: Optional[str] = None) -> boto3.session.Session:
    if profile:
        return boto3.session.Session(profile_name=profile)
    return boto3.session.Session()


def get_asg_client(session: boto3.session.Session, region: Optional[str] = None):
    cfg = Config(retries={"max_attempts": 10, "mode": "standard"})
    return session.client("autoscaling", region_name=region, config=cfg)


def list_asgs(session: boto3.session.Session, region: Optional[str]) -> List[AsgInfo]:
    client = get_asg_client(session, region)
    paginator = client.get_paginator("describe_auto_scaling_groups")
    asgs: List[AsgInfo] = []
    for page in paginator.paginate():
        for g in page.get("AutoScalingGroups", []):
            asgs.append(
                AsgInfo(
                    name=g["AutoScalingGroupName"],
                    min_size=g.get("MinSize", 0),
                    max_size=g.get("MaxSize", 0),
                    desired_capacity=g.get("DesiredCapacity", 0),
                )
            )
    return asgs


def apply_plan(session: boto3.session.Session, region: Optional[str], updates: Iterable[CapacityUpdate]) -> None:
    client = get_asg_client(session, region)
    log = get_logger()
    for upd in updates:
        kwargs = {"AutoScalingGroupName": upd.name}
        if upd.min_size is not None:
            kwargs["MinSize"] = upd.min_size
        if upd.max_size is not None:
            kwargs["MaxSize"] = upd.max_size
        if upd.desired is not None:
            kwargs["DesiredCapacity"] = upd.desired
        if len(kwargs) > 1:
            log.info("asg.update", **{k: v for k, v in kwargs.items() if k != "AutoScalingGroupName"}, name=upd.name)
            client.update_auto_scaling_group(**kwargs)


