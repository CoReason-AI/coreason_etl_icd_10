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
from unittest.mock import MagicMock, patch

import pytest

from coreason_etl_icd_10.config import DiagnosticConfigManifest
from coreason_etl_icd_10.main import EpistemicOrchestrationIntent, main


@patch("coreason_etl_icd_10.main.dlt.pipeline")
@patch("coreason_etl_icd_10.main.fetch_icd10_cm_raw")
def test_run_dlt_pipeline(mock_fetch: MagicMock, mock_pipeline: MagicMock) -> None:
    """Validate that the DLT pipeline runs properly."""
    manifest = DiagnosticConfigManifest()
    mock_pipe_instance = MagicMock()
    mock_pipeline.return_value = mock_pipe_instance
    mock_pipe_instance.run.return_value = "Mock Load Info"
    mock_fetch.return_value = ["mock_data"]

    EpistemicOrchestrationIntent.run_dlt_pipeline(manifest)

    mock_pipeline.assert_called_once_with(
        pipeline_name="coreason_etl_icd10",
        destination="postgres",
        dataset_name="bronze",
    )
    mock_pipe_instance.run.assert_called_once_with(["mock_data"])


@patch("coreason_etl_icd_10.main.subprocess.run")
@patch("coreason_etl_icd_10.main.Path.exists")
def test_run_dbt_transformations_success(mock_exists: MagicMock, mock_run: MagicMock) -> None:
    """Validate that DBT transformations trigger correctly."""
    mock_exists.return_value = True
    mock_run.return_value = subprocess.CompletedProcess(args=[], returncode=0, stdout="Success", stderr="")

    EpistemicOrchestrationIntent.run_dbt_transformations()

    mock_run.assert_called_once()
    assert "dbt" in mock_run.call_args[0][0]
    assert "run" in mock_run.call_args[0][0]


@patch("coreason_etl_icd_10.main.Path.exists")
def test_run_dbt_transformations_no_dir(mock_exists: MagicMock) -> None:
    """Validate behavior when DBT directory is missing."""
    mock_exists.return_value = False

    with pytest.raises(FileNotFoundError, match="DBT project directory not found"):
        EpistemicOrchestrationIntent.run_dbt_transformations()


@patch("coreason_etl_icd_10.main.subprocess.run")
@patch("coreason_etl_icd_10.main.Path.exists")
def test_run_dbt_transformations_error(mock_exists: MagicMock, mock_run: MagicMock) -> None:
    """Validate that DBT execution errors are handled properly."""
    mock_exists.return_value = True
    mock_run.side_effect = subprocess.CalledProcessError(returncode=1, cmd=["dbt", "run"], stderr="Mock Error")

    with pytest.raises(RuntimeError, match="DBT run failed with exit code 1"):
        EpistemicOrchestrationIntent.run_dbt_transformations()


@patch("coreason_etl_icd_10.main.EpistemicOrchestrationIntent.run_dlt_pipeline")
@patch("coreason_etl_icd_10.main.EpistemicOrchestrationIntent.run_dbt_transformations")
def test_main_success(mock_run_dbt: MagicMock, mock_run_dlt: MagicMock) -> None:
    """Validate orchestration main flow."""
    main()

    mock_run_dlt.assert_called_once()
    mock_run_dbt.assert_called_once()


@patch("coreason_etl_icd_10.main.EpistemicOrchestrationIntent.run_dlt_pipeline")
def test_main_exception_handling(mock_run_dlt: MagicMock) -> None:
    """Validate exception handling in main orchestration."""
    mock_run_dlt.side_effect = ValueError("Mock dlt error")

    with pytest.raises(ValueError, match="Mock dlt error"):
        main()
