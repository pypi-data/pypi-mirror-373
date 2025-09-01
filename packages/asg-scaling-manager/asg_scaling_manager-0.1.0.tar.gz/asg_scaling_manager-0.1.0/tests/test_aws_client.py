from asg_scaling_manager.models import CapacityUpdate
from asg_scaling_manager.aws_client import apply_plan


class FakeClient:
    def __init__(self):
        self.calls = []

    def update_auto_scaling_group(self, **kwargs):
        self.calls.append(kwargs)


def test_apply_plan_sends_expected_calls(monkeypatch):
    fake = FakeClient()

    def fake_get_asg_client(sess, region=None):
        return fake

    monkeypatch.setattr("asg_scaling_manager.aws_client.get_asg_client", fake_get_asg_client)

    updates = [
        CapacityUpdate(name="asg-a", desired=2),
        CapacityUpdate(name="asg-b", min_size=1, max_size=5, desired=3),
    ]

    apply_plan(object(), None, updates)

    assert fake.calls == [
        {"AutoScalingGroupName": "asg-a", "DesiredCapacity": 2},
        {"AutoScalingGroupName": "asg-b", "MinSize": 1, "MaxSize": 5, "DesiredCapacity": 3},
    ]


