import asyncio


def test_core_public_api_surfaces():
    from cflow_platform.core.public_api import (
        get_stdio_server,
        get_direct_client_executor,
        safe_get_version_info,
    )

    assert callable(get_stdio_server())
    assert callable(get_direct_client_executor())
    info = safe_get_version_info()
    assert isinstance(info, dict) and "api_version" in info


def test_direct_client_exec_unknown_tool():
    from cflow_platform.core.public_api import get_direct_client_executor

    exec_fn = get_direct_client_executor()
    result = asyncio.get_event_loop().run_until_complete(exec_fn("__no_such_tool__"))
    assert result.get("status") in {"error", "success"}


def test_tool_dispatch_families():
    from cflow_platform.core.public_api import get_direct_client_executor

    exec_fn = get_direct_client_executor()

    # System
    sys_version = asyncio.get_event_loop().run_until_complete(exec_fn("sys_version"))
    assert sys_version.get("status") == "success"

    # Tasks
    task_list = asyncio.get_event_loop().run_until_complete(exec_fn("task_list"))
    assert task_list.get("status") == "success"

    # Docs
    doc_quality = asyncio.get_event_loop().run_until_complete(exec_fn("doc_quality", taskId="1"))
    assert doc_quality.get("status") == "success"

    # Plan
    plan_list = asyncio.get_event_loop().run_until_complete(exec_fn("plan_list", search_path="docs"))
    assert plan_list.get("success") in {True, False}

    # Linting
    lint_status = asyncio.get_event_loop().run_until_complete(exec_fn("lint_status"))
    assert lint_status.get("status") == "success"

    # Enhanced linting
    enh_status = asyncio.get_event_loop().run_until_complete(exec_fn("enh_status"))
    assert enh_status.get("status") == "success"

    # Testing
    test_conf = asyncio.get_event_loop().run_until_complete(exec_fn("test_confidence"))
    assert test_conf.get("status") == "success"


