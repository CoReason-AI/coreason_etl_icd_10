# Copyright (c) 2026 CoReason, Inc.
#
# This software is proprietary and dual-licensed.
# Licensed under the Prosperity Public License 3.0 (the "License").
# A copy of the license is available at https://prosperitylicense.com/versions/3.0.0
# For details, see the LICENSE file.
# Commercial use beyond a 30-day trial requires a separate license.
#
# Source Code: https://github.com/CoReason-AI/coreason_etl_icd_10

"""
Test suite validating the Epistemic HTTP Client utilities.
"""

import pytest
import requests
import responses

from coreason_etl_icd_10.utils.http_client import EpistemicHttpClient


@responses.activate
def test_epistemic_http_client_success() -> None:
    """Validate that the EpistemicHttpClient returns the correct response payload and uses headers."""
    test_url = "https://example.com/api"
    mock_payload = b"mock content"

    responses.add(
        responses.GET,
        test_url,
        body=mock_payload,
        status=200,
    )

    response = EpistemicHttpClient.get(test_url)

    assert response.status_code == 200
    assert response.content == mock_payload

    # Assert headers
    assert len(responses.calls) == 1
    assert "User-Agent" in responses.calls[0].request.headers
    assert responses.calls[0].request.headers["User-Agent"].startswith("Mozilla/5.0")


@responses.activate
def test_epistemic_http_client_http_error() -> None:
    """Validate that the EpistemicHttpClient raises exceptions correctly for bad responses."""
    test_url = "https://example.com/api"

    responses.add(
        responses.GET,
        test_url,
        status=403,
        json={"error": "forbidden"},
    )

    with pytest.raises(requests.exceptions.HTTPError):
        EpistemicHttpClient.get(test_url)
