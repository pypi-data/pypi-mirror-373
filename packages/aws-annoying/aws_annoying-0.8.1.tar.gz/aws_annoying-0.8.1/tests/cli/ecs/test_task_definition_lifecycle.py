from __future__ import annotations

from typing import TYPE_CHECKING

import boto3
import pytest
from typer.testing import CliRunner

from aws_annoying.cli.main import app
from tests.cli._helpers import normalize_console_output

if TYPE_CHECKING:
    from pytest_snapshot.plugin import Snapshot

runner = CliRunner()

pytestmark = [
    pytest.mark.unit,
    pytest.mark.usefixtures("use_moto"),
]


def test_basic(snapshot: Snapshot) -> None:
    """The command should deregister the oldest task definitions."""
    # Arrange
    ecs = boto3.client("ecs")
    family = "my-task"
    num_task_defs = 25
    for i in range(1, num_task_defs + 1):
        ecs.register_task_definition(
            family=family,
            containerDefinitions=[
                {
                    "name": "my-container",
                    "image": f"my-image:{i}",
                    "cpu": 0,
                    "memory": 0,
                },
            ],
        )

    # Act
    keep_latest = 10
    result = runner.invoke(
        app,
        [
            "ecs",
            "task-definition-lifecycle",
            "--family",
            family,
            "--keep-latest",
            str(keep_latest),
        ],
    )

    # Assert
    assert result.exit_code == 0
    snapshot.assert_match(normalize_console_output(result.stdout), "stdout.txt")

    active_task_definitions = ecs.list_task_definitions(familyPrefix=family, status="ACTIVE")
    assert active_task_definitions["taskDefinitionArns"] == [
        f"arn:aws:ecs:us-east-1:123456789012:task-definition/{family}:{i}" for i in range(16, 26)
    ]

    inactive_task_definitions = ecs.list_task_definitions(familyPrefix=family, status="INACTIVE")
    assert inactive_task_definitions["taskDefinitionArns"] == [
        f"arn:aws:ecs:us-east-1:123456789012:task-definition/{family}:{i}" for i in range(1, 16)
    ]


def test_delete(snapshot: Snapshot) -> None:
    """The command should deregister the oldest task definitions."""
    # Arrange
    ecs = boto3.client("ecs")
    family = "my-task"
    num_task_defs = 25
    for i in range(1, num_task_defs + 1):
        ecs.register_task_definition(
            family=family,
            containerDefinitions=[
                {
                    "name": "my-container",
                    "image": f"my-image:{i}",
                    "cpu": 0,
                    "memory": 0,
                },
            ],
        )

    # Act
    keep_latest = 10
    result = runner.invoke(
        app,
        [
            "ecs",
            "task-definition-lifecycle",
            "--family",
            family,
            "--keep-latest",
            str(keep_latest),
            "--delete",
        ],
    )

    # Assert
    assert result.exit_code == 0
    snapshot.assert_match(normalize_console_output(result.stdout), "stdout.txt")

    active_task_definitions = ecs.list_task_definitions(familyPrefix=family, status="ACTIVE")
    assert active_task_definitions["taskDefinitionArns"] == [
        f"arn:aws:ecs:us-east-1:123456789012:task-definition/{family}:{i}" for i in range(16, 26)
    ]

    inactive_task_definitions = ecs.list_task_definitions(familyPrefix=family, status="INACTIVE")
    assert inactive_task_definitions["taskDefinitionArns"] == []


def test_dry_run(snapshot: Snapshot) -> None:
    """If `--dry-run` option given, the command should not perform any changes."""
    # Arrange
    ecs = boto3.client("ecs")
    family = "my-task"
    num_task_defs = 25
    for i in range(1, num_task_defs + 1):
        ecs.register_task_definition(
            family=family,
            containerDefinitions=[
                {
                    "name": "my-container",
                    "image": f"my-image:{i}",
                    "cpu": 0,
                    "memory": 0,
                },
            ],
        )

    # Act
    keep_latest = 10
    result = runner.invoke(
        app,
        [
            "--dry-run",
            "ecs",
            "task-definition-lifecycle",
            "--family",
            family,
            "--keep-latest",
            str(keep_latest),
            "--delete",
        ],
    )

    # Assert
    assert result.exit_code == 0
    snapshot.assert_match(normalize_console_output(result.stdout), "stdout.txt")

    active_task_definitions = ecs.list_task_definitions(familyPrefix=family, status="ACTIVE")
    assert len(active_task_definitions["taskDefinitionArns"]) == 25

    inactive_task_definitions = ecs.list_task_definitions(familyPrefix=family, status="INACTIVE")
    assert len(inactive_task_definitions["taskDefinitionArns"]) == 0
