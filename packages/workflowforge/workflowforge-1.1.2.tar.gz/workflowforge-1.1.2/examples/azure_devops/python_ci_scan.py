#!/usr/bin/env python3
"""
Generate an Azure DevOps Python CI matrix pipeline and run an optional
Checkov scan against the emitted YAML (if Checkov is installed).
"""

from workflowforge import azure_devops as ado


def main() -> None:
    pipeline = ado.python_ci_template_azure(
        python_versions=["3.11", "3.12", "3.13"],
        os_list=["ubuntu-latest", "windows-latest", "macOS-latest"],
        use_cache=True,
    )

    out_path = "examples/azure_devops/azure-pipelines-scan.yml"
    pipeline.save(out_path, scan_with_checkov=True)
    print(f"✅ Azure DevOps pipeline created and scanned (if available): {out_path}")


if __name__ == "__main__":
    main()
