# Copyright (c) 2026 CoReason, Inc.
#
# This software is proprietary and dual-licensed.
# Licensed under the Prosperity Public License 3.0 (the "License").
# A copy of the license is available at https://prosperitylicense.com/versions/3.0.0
# For details, see the LICENSE file.
# Commercial use beyond a 30-day trial requires a separate license.
#
# Source Code: https://github.com/CoReason-AI/coreason_etl_icd_10

import subprocess
from pathlib import Path

import dlt

from coreason_etl_icd_10.config import DiagnosticConfigManifest
from coreason_etl_icd_10.pipeline import fetch_icd10_cm_raw
from coreason_etl_icd_10.utils.logger import logger


class EpistemicOrchestrationIntent:
    """
    EpistemicOrchestrationIntent to execute the ingestion pipeline and DBT transformations.

    AGENT INSTRUCTION: This class deterministically manages the orchestration of the dlt pipeline
    and subsequently triggers dbt transformations via a subprocess execution.
    """

    @staticmethod
    def run_dlt_pipeline(manifest: DiagnosticConfigManifest) -> dlt.Pipeline:
        """Runs the DLT pipeline to fetch and load raw CMS data into the bronze layer."""
        logger.info("Initializing EpistemicOrchestrationIntent: DLT Pipeline Execution")

        pipeline = dlt.pipeline(
            pipeline_name="coreason_etl_icd10",
            destination="postgres",
            dataset_name="bronze",
        )

        # Execute the pipeline with the specific resource
        load_info = pipeline.run(fetch_icd10_cm_raw(manifest))
        logger.info(f"DLT Pipeline execution completed. Load Info:\n{load_info}")

        return pipeline

    @staticmethod
    def run_dbt_transformations() -> None:
        """Programmatically triggers the dbt transformations for silver and gold layers."""
        logger.info("Triggering DBT transformations...")

        # Find the path to the dbt project relative to the current file
        dbt_project_dir = Path(__file__).parent.parent / "dbt_project"

        if not dbt_project_dir.exists():
            raise FileNotFoundError(f"DBT project directory not found at: {dbt_project_dir}")

        # Construct the dbt run command
        cmd = ["dbt", "run", "--project-dir", str(dbt_project_dir)]

        try:
            # We use subprocess.run to execute dbt as a shell command
            # The output and errors are captured
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)  # noqa: S603
            logger.info("DBT transformations completed successfully.")
            logger.debug(f"DBT Output:\n{result.stdout}")
        except subprocess.CalledProcessError as e:
            logger.error("DBT execution failed.")
            logger.error(f"DBT Error Output:\n{e.stderr}")
            raise RuntimeError(f"DBT run failed with exit code {e.returncode}") from e


def main() -> None:
    """Main entry point for pipeline orchestration."""
    try:
        # 1. Initialize configuration
        manifest = DiagnosticConfigManifest()

        # 2. Run Ingestion (DLT)
        EpistemicOrchestrationIntent.run_dlt_pipeline(manifest)

        # 3. Run Transformations (DBT)
        EpistemicOrchestrationIntent.run_dbt_transformations()

        logger.info("Pipeline orchestration completed successfully.")

    except Exception as e:
        logger.exception("Pipeline orchestration encountered an epistemic failure.")
        raise e


if __name__ == "__main__":  # pragma: no cover
    main()
