#!/usr/bin/env python3
"""
Generate an Azure DevOps Python CI matrix pipeline using WorkflowForge.
"""

from workflowforge import azure_devops as ado


def main() -> None:
    pipeline = ado.python_ci_template_azure(
        python_versions=["3.11", "3.12", "3.13"],
        branches=["main"],
        os_list=["ubuntu-latest", "windows-latest", "macOS-latest"],
        use_cache=True,
    )
    pipeline.save("examples/azure_devops/python_ci.yml")
    print("✅ Azure DevOps pipeline created: examples/azure_devops/python_ci.yml")


if __name__ == "__main__":
    main()
