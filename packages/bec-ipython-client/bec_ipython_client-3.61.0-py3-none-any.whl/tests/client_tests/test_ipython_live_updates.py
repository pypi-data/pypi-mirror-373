from unittest import mock

import pytest

from bec_ipython_client.callbacks.ipython_live_updates import IPythonLiveUpdates
from bec_lib import messages
from bec_lib.queue_items import QueueItem


@pytest.mark.timeout(20)
def test_live_updates_process_queue_pending(bec_client_mock):
    client = bec_client_mock
    live_updates = IPythonLiveUpdates(client)
    request_msg = messages.ScanQueueMessage(
        scan_type="grid_scan",
        parameter={"args": {"samx": (-5, 5, 3)}, "kwargs": {}},
        queue="primary",
        metadata={"RID": "something"},
    )
    queue = QueueItem(
        scan_manager=client.queue,
        queue_id="queue_id",
        request_blocks=[request_msg],
        status="PENDING",
        active_request_block={},
        scan_id=["scan_id"],
    )
    client.queue.queue_storage.current_scan_queue = {"primary": {"status": "RUNNING"}}
    with mock.patch.object(queue, "_update_with_buffer"):
        with mock.patch(
            "bec_lib.queue_items.QueueItem.queue_position", new_callable=mock.PropertyMock
        ) as queue_pos:
            queue_pos.return_value = 2
            with mock.patch.object(
                live_updates,
                "_available_req_blocks",
                return_value=[{"report_instructions": [], "content": {"scan_type": "grid_scan"}}],
            ):
                with mock.patch.object(live_updates, "_process_report_instructions") as process:
                    with mock.patch("builtins.print") as prt:
                        res = live_updates._process_queue(queue, request_msg, "req_id")
                        prt.assert_called_once()
                        process.assert_not_called()
                    assert res is False


@pytest.mark.timeout(20)
def test_live_updates_process_queue_running(bec_client_mock):
    client = bec_client_mock
    live_updates = IPythonLiveUpdates(client)
    request_msg = messages.ScanQueueMessage(
        scan_type="grid_scan",
        parameter={"args": {"samx": (-5, 5, 3)}, "kwargs": {}},
        queue="primary",
        metadata={"RID": "something"},
    )
    queue = QueueItem(
        scan_manager=client.queue,
        queue_id="queue_id",
        request_blocks=[request_msg],
        status="RUNNING",
        active_request_block={},
        scan_id=["scan_id"],
    )
    live_updates._active_request = request_msg
    client.queue.queue_storage.current_scan_queue = {"primary": {"status": "RUNNING"}}
    with mock.patch.object(queue, "_update_with_buffer"):
        with mock.patch(
            "bec_lib.queue_items.QueueItem.queue_position", new_callable=mock.PropertyMock
        ) as queue_pos:
            queue_pos.return_value = 2
            with mock.patch.object(
                live_updates,
                "_available_req_blocks",
                return_value=[
                    {
                        "report_instructions": [{"wait_table": 10}],
                        "content": {"scan_type": "grid_scan"},
                    }
                ],
            ):
                with mock.patch.object(live_updates, "_process_instruction") as process:
                    with mock.patch("builtins.print") as prt:
                        res = live_updates._process_queue(queue, request_msg, "req_id")
                        prt.assert_not_called()
                        process.assert_called_once_with({"wait_table": 10})
                    assert res is True


@pytest.mark.timeout(20)
def test_live_updates_process_queue_without_status(bec_client_mock):
    client = bec_client_mock
    live_updates = IPythonLiveUpdates(client)
    request_msg = messages.ScanQueueMessage(
        scan_type="grid_scan",
        parameter={"args": {"samx": (-5, 5, 3)}, "kwargs": {}},
        queue="primary",
        metadata={"RID": "something"},
    )
    queue = QueueItem(
        scan_manager=client.queue,
        queue_id="queue_id",
        request_blocks=[request_msg],
        status=None,
        active_request_block={},
        scan_id=["scan_id"],
    )
    with mock.patch.object(queue, "_update_with_buffer"):
        assert live_updates._process_queue(queue, request_msg, "req_id") is False


@pytest.mark.timeout(20)
def test_live_updates_process_queue_without_queue_number(bec_client_mock):
    client = bec_client_mock
    live_updates = IPythonLiveUpdates(client)
    request_msg = messages.ScanQueueMessage(
        scan_type="grid_scan",
        parameter={"args": {"samx": (-5, 5, 3)}, "kwargs": {}},
        queue="primary",
        metadata={"RID": "something"},
    )

    with mock.patch(
        "bec_lib.queue_items.QueueItem.queue_position", new_callable=mock.PropertyMock
    ) as queue_pos:
        queue = QueueItem(
            scan_manager=client.queue,
            queue_id="queue_id",
            request_blocks=[request_msg],
            status="PENDING",
            active_request_block={},
            scan_id=["scan_id"],
        )
        queue_pos.return_value = None
        with mock.patch.object(queue, "_update_with_buffer"):
            assert live_updates._process_queue(queue, request_msg, "req_id") is False


# @pytest.mark.timeout(20)
# @pytest.mark.asyncio
# def test_live_updates_process_instruction_readback(bec_client_mock):
#     client = bec_client_mock
#     live_updates = IPythonLiveUpdates(client)
#     request_msg = messages.ScanQueueMessage(
#         scan_type="grid_scan",
#         parameter={"args": {"samx": (-5, 5, 3)}, "kwargs": {}},
#         queue="primary",
#         metadata={"RID": "something"},
#     )
#     live_updates._active_request = request_msg
#     live_updates._user_callback = []
#     client.queue.queue_storage.current_scan_queue = {"primary": {"status": "RUNNING"}}
#     with mock.patch(
#         "bec_client_mock.callbacks.ipython_live_updates.LiveUpdatesTable", new_callable=mock.Co
#     ) as table:
#         live_updates._process_instruction({"scan_progress": 10})
#         table.assert_called_once_with(
#             client, report_instructions={"scan_progress": 10}, request=request_msg, callbacks=[]
#         )
