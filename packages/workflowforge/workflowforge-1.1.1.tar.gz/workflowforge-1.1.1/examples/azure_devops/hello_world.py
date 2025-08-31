#!/usr/bin/env python3
"""
Generate a minimal Azure DevOps pipeline that prints a hello message.
"""

from workflowforge import azure_devops as ado


def main() -> None:
    pipeline = ado.hello_world_template_azure(
        name="Hello ADO",
        message="Hello Azure DevOps from WorkflowForge!",
        vm_image="ubuntu-latest",
        branches=["main"],
    )
    pipeline.save("examples/azure_devops/hello_world.yml")
    print(
        "✅ Azure DevOps hello pipeline created: examples/azure_devops/hello_world.yml"
    )


if __name__ == "__main__":
    main()
