import typer
from typing import Optional
from .logging import get_logger
from .aws_client import create_session, get_asg_client, apply_plan
from .models import Plan, AsgInfo
from .planner import plan_equal_split, plan_zero

app = typer.Typer(help="Manage ASG capacities by tag filters")


@app.command()
def set_capacity(
    tag_key: str = typer.Option("eks:cluster-name", help="Tag key to filter ASGs"),
    tag_value: str = typer.Option(..., help="Tag value to filter ASGs"),
    desired: int = typer.Option(..., help="Desired instances total across matched ASGs (0 allowed)"),
    max_size: Optional[int] = typer.Option(None, help="Optional max size cap to apply to each ASG"),
    name_contains: Optional[str] = typer.Option(None, help="Further filter: ASG name contains string"),
    profile: Optional[str] = typer.Option(None, help="AWS profile name to use"),
    region: Optional[str] = typer.Option(None, help="AWS region (overrides profile default)"),
    dry_run: bool = typer.Option(False, help="Do not perform updates, only log actions"),
):
    """Distribute desired capacity across ASGs with the given tag."""
    log = get_logger()
    log.info(
        "cli.args",
        tag_key=tag_key,
        tag_value=tag_value,
        desired=desired,
        max_size=max_size,
        name_contains=name_contains,
        profile=profile,
        region=region,
        dry_run=dry_run,
    )
    if desired < 0:
        typer.echo("Desired must be >= 0")
        raise typer.Exit(code=2)

    # Build AWS session and pre-filter ASGs by tag at source
    sess = create_session(profile)
    asg_client = get_asg_client(sess, region)
    paginator = asg_client.get_paginator("describe_auto_scaling_groups")
    matched = []
    for page in paginator.paginate():
        for g in page.get("AutoScalingGroups", []):
            tags = {t.get("Key"): t.get("Value") for t in g.get("Tags", [])}
            if tags.get(tag_key) != tag_value:
                continue
            name = g["AutoScalingGroupName"]
            if name_contains and name_contains not in name:
                continue
            matched.append(
                AsgInfo(
                    name=name,
                    min_size=g.get("MinSize", 0),
                    max_size=g.get("MaxSize", 0),
                    desired_capacity=g.get("DesiredCapacity", 0),
                )
            )

    if not matched:
        typer.echo("No ASGs matched the provided filters.")
        raise typer.Exit(code=1)

    # Plan
    if desired == 0:
        plan: Plan = plan_zero(matched)
    else:
        plan = plan_equal_split(matched, desired, max_size)

    # Report
    for u in plan.updates:
        log.info(
            "plan.update",
            name=u.name,
            desired=u.desired,
            min_size=u.min_size,
            max_size=u.max_size,
        )

    # Warn if plan cannot reach desired total
    planned_total = plan.total_desired
    if planned_total < desired:
        msg = (
            f"Planned total desired {planned_total} is less than requested {desired}. "
            "This may be due to per-ASG caps or current MaxSize limits."
        )
        log.warning("plan.cap_limited", planned_total=planned_total, requested=desired)
        typer.echo(msg)

    if dry_run:
        typer.echo("[DRY-RUN] No changes applied.")
        return

    # Apply
    apply_plan(sess, region, plan.updates)
    typer.echo("Updates submitted.")


if __name__ == "__main__":
    app()


