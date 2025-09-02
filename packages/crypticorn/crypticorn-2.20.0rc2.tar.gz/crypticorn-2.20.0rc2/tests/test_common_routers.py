import re

import pytest


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "path,expected_status,expected_pattern",
    [
        ("/", 200, r'^"OK"$'),
        ("/time?type=iso", 200, r'^"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}'),
        ("/time?type=unix", 200, r'^"\d+"$'),
        ("/admin/uptime?type=seconds", 200, r'^"\d+"$'),
        ("/admin/uptime?type=human", 200, r'^"\d{2}:\d{2}:\d{2}"$'),
        ("/admin/memory", 200, r"^\d+\.?\d*$"),
        ("/admin/threads", 200, None),
        ("/admin/limits", 200, None),
        ("/admin/dependencies", 200, None),
    ],
)
async def test_common_router_endpoints(client, path, expected_status, expected_pattern):
    response = await client.get(path)
    assert response.status_code == expected_status

    if expected_pattern:
        assert re.match(expected_pattern, response.text)
    else:
        assert response.headers.get("content-type", "").startswith("application/json")
        json_data = response.json()
        assert isinstance(json_data, (dict, list))


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "path,expected_status",
    [
        ("/time?type=invalid", 422),
        ("/admin/uptime?type=invalid", 422),
        ("/nonexistent", 404),
    ],
)
async def test_common_router_error_cases(client, path, expected_status):
    response = await client.get(path)
    assert response.status_code == expected_status


@pytest.mark.asyncio
async def test_admin_dependencies_filtering(client):
    response = await client.get("/admin/dependencies?include=fastapi&include=pytest")
    assert response.status_code == 200
    deps = response.json()
    assert isinstance(deps, dict)

    response = await client.get("/admin/dependencies")
    assert response.status_code == 200
    all_deps = response.json()
    assert isinstance(all_deps, dict)
    assert len(all_deps) >= len(deps)


@pytest.mark.asyncio
async def test_admin_log_level_deprecated(client):
    response = await client.get("/admin/log-level")
    assert response.status_code == 200
    log_level = response.text.strip('"')
    assert log_level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "path,expected_status,expected_text",
    [
        ("/", 200, '"OK"'),
    ],
)
async def test_ping_endpoint(client, path, expected_status, expected_text):
    response = await client.get(path)
    assert response.status_code == expected_status
    assert response.text == expected_text


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "type_param,expected_status",
    [
        ("iso", 200),
        ("unix", 200),
    ],
)
async def test_time_endpoint_valid_types(client, type_param, expected_status):
    response = await client.get(f"/time?type={type_param}")
    assert response.status_code == expected_status
    body = response.text
    if type_param == "iso":
        assert re.match(r'^"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}', body)
    else:
        # Unix timestamp is returned as quoted string
        assert re.match(r'^"\d+"$', body)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "type_param,expected_status",
    [
        ("invalid", 422),
        ("123", 422),
    ],
)
async def test_time_endpoint_invalid_types(client, type_param, expected_status):
    response = await client.get(f"/time?type={type_param}")
    assert response.status_code == expected_status
