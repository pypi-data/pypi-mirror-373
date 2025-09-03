import datetime
import json
import subprocess
from pathlib import Path
from typing import Any

import yaml


def main(tf_dir: Path, service_module_name: str):
    tf_state = load_tf_state(tf_dir)

    def get_state(address: str):
        abs_path = f"module.{service_module_name}.{address}"
        for child_module in tf_state["values"]["root_module"]["child_modules"]:
            for resource in child_module["resources"]:
                if resource["address"] == abs_path:
                    return resource

        print(f"\033[1;31m!! Resource {address} not found in Terraform state.")
        print()
        sys.exit(1)

    def get_value(address: str, key: str):
        state = get_state(address)
        if state:
            return state["values"].get(key)
        else:
            print(
                f"\033[1;31m!! Resource {address} has no value '{key}' in Terraform state."
            )
            print()
            sys.exit(1)

    lb_dns_name = get_value("aws_lb.service", "dns_name")
    ecs_cluster_arn = get_value("aws_ecs_service.service[0]", "cluster")
    ecs_service_id = get_value("aws_ecs_service.service[0]", "id")
    expected_task_definition_arn = get_value(
        "aws_ecs_service.service[0]", "task_definition"
    )

    print()
    print(f"             Load Balancer:  {lb_dns_name}")
    print(f"               ECS Cluster:  {ecs_cluster_arn}")
    print(f"               ECS Service:  {ecs_service_id}")
    print(f"  Expected Task Definition:  {expected_task_definition_arn}")
    print()

    service_info = describe_ecs_service(ecs_cluster_arn, ecs_service_id)

    deployments = sorted(
        service_info["deployments"], key=lambda d: d["createdAt"], reverse=True
    )

    for deployment in deployments:
        task_definition_arn = deployment["taskDefinition"]
        task_definition = describe_ecs_task_definition(task_definition_arn)
        container_definition = task_definition["containerDefinitions"][0]

        started_at = datetime.datetime.fromisoformat(deployment["createdAt"])
        updated_at = datetime.datetime.fromisoformat(deployment["updatedAt"])

        svcconfig_yaml = next(
            (
                env["value"]
                for env in container_definition["environment"]
                if env["name"] == "SVCCONFIG_DATA"
            ),
        )

        image = container_definition["image"]

        if deployment["rolloutState"] == "COMPLETED":
            print(f"\033[1;32mDeployment completed at {updated_at}:\033[0m")
        else:
            print(f"\033[1mDeployment started at {started_at}:\033[0m")
        print()

        print(f"           Status:  {deployment['status']}")
        print(f"  Task Definition:  {task_definition_arn}")
        if expected_task_definition_arn == task_definition_arn:
            print(
                f"                    (this is the same version as the task definition from the Terraform state)"
            )
        print(f"            Image:  {image}")
        print(f"          Rollout:  {deployment['rolloutStateReason']}")
        print(f"                      desired: {deployment['desiredCount']}")
        print(f"                      pending: {deployment['pendingCount']}")
        print(f"                      running: {deployment['runningCount']}")

        svcconfig = yaml.load(svcconfig_yaml, Loader=yaml.Loader)
        print(
            "   Service Config:  "
            + json.dumps(svcconfig, indent=2).replace("\n", "\n                    ")
        )

        print()


def describe_ecs_task_definition(
    task_definition_arn: str,
) -> dict[str, Any]:
    ecs_result = subprocess.run(
        [
            "aws",
            "ecs",
            "describe-task-definition",
            "--task-definition",
            task_definition_arn,
        ],
        capture_output=True,
        text=True,
    )

    if ecs_result.returncode != 0:
        print()
        print("\033[1;31m!! Error running `aws ecs describe-task-definition`:\033[0m")
        print()
        print(ecs_result.stderr)
        sys.exit(1)

    return json.loads(ecs_result.stdout)["taskDefinition"]


def describe_ecs_service(
    cluster_arn: str,
    service_id: str,
) -> dict[str, Any]:
    ecs_result = subprocess.run(
        [
            "aws",
            "ecs",
            "describe-services",
            "--cluster",
            cluster_arn,
            "--services",
            service_id,
        ],
        capture_output=True,
        text=True,
    )

    if ecs_result.returncode != 0:
        print()
        print("\033[1;31m!! Error running `aws ecs describe-services`:\033[0m")
        print()
        print(ecs_result.stderr)
        sys.exit(1)

    return json.loads(ecs_result.stdout)["services"][0]


def load_tf_state(tf_dir: Path) -> dict[str, Any]:
    tf_result = subprocess.run(
        ["terraform", "show", "-json"],
        cwd=tf_dir,
        capture_output=True,
        text=True,
    )

    if tf_result.returncode != 0:
        print()
        print("\033[1;31m!! Error running `terraform show`:\033[0m")
        print()
        print(tf_result.stderr)
        if "failed to refresh cached credentials" in tf_result.stderr:
            print(
                "\033[1;33mDo you have the correct AWS credentials set up, e.g.is AWS_PROFILE set?\033[0m"
            )
            print()
        sys.exit(1)

    return json.loads(tf_result.stdout)


if __name__ == "__main__":
    import sys

    # Check if the script is being run with the correct argument
    if len(sys.argv) not in (2, 3):
        print("Usage: python debug.py <terraform_directory> [<service module name>]")
        sys.exit(1)

    terraform_directory = sys.argv[1]
    service_module_name = sys.argv[2] if len(sys.argv) == 3 else "service"

    main(Path(terraform_directory), service_module_name)
