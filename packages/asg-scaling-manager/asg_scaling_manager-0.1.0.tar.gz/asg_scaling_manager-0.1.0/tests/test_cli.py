import json
from typer.testing import CliRunner

from asg_scaling_manager.cli import app


runner = CliRunner()


def test_cli_requires_arguments():
    result = runner.invoke(app, [])
    assert result.exit_code != 0


def test_cli_dry_run(monkeypatch):
    # Mock AWS calls
    class FakePaginator:
        def paginate(self):
            yield {
                "AutoScalingGroups": [
                    {
                        "AutoScalingGroupName": "asg-a",
                        "MinSize": 0,
                        "MaxSize": 10,
                        "DesiredCapacity": 0,
                        "Tags": [{"Key": "env", "Value": "test"}],
                    },
                    {
                        "AutoScalingGroupName": "asg-b",
                        "MinSize": 0,
                        "MaxSize": 10,
                        "DesiredCapacity": 0,
                        "Tags": [{"Key": "env", "Value": "test"}],
                    },
                ]
            }

    class FakeClient:
        def get_paginator(self, _):
            return FakePaginator()

    def fake_create_session(profile=None):
        return object()

    def fake_get_asg_client(sess, region=None):
        return FakeClient()

    monkeypatch.setattr("asg_scaling_manager.cli.create_session", fake_create_session)
    monkeypatch.setattr("asg_scaling_manager.cli.get_asg_client", fake_get_asg_client)

    result = runner.invoke(
        app,
        [
            "--tag-key",
            "env",
            "--tag-value",
            "test",
            "--desired",
            "4",
            "--dry-run",
        ],
    )
    assert result.exit_code == 0, result.output
    assert "[DRY-RUN] No changes applied." in result.output


