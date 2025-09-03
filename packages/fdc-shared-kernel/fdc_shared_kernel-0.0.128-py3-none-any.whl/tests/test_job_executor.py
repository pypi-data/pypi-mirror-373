"""
Author: Akdham
Filename: test_job_executor.py
Description: Unit tests for job_executor.py
Date: 2025-05-07
"""
import json
import unittest
from unittest.mock import MagicMock, ANY
from shared_kernel.enums import TaskStatus
from shared_kernel.event_executor.job_executor import JobExecutor
from shared_kernel.messaging.utils.event_messages import AWSEventMessage


def get_fake_event_message():
    event_dict = {
        "Body": json.dumps(
            {
                "detail": {
                    "event_name": "TEST_EVENT",
                    "event_payload": {"id": "123"},
                    "event_meta": {
                        "trace_id": "trace-abc",
                        "job_id": "job-123",
                        "trigger": "MANUAL",
                        "org_id": "9999",
                    },
                }
            }
        ),
        "ReceiptHandle": "dummy-receipt-handle",
    }
    return AWSEventMessage(event_dict)


class TestJobExecutor(unittest.TestCase):
    def setUp(self):
        self.mock_status_tracker = MagicMock()
        self.mock_databus = MagicMock()
        self.job_executor = JobExecutor(
            status_tracker=self.mock_status_tracker, databus=self.mock_databus
        )

        self.mock_event_msg = get_fake_event_message()

    def test_submit_job_success(self):
        """Test successful job submission."""
        self.mock_status_tracker.get_task.return_value = None

        mock_callback = MagicMock()
        self.job_executor.submit_job(mock_callback, self.mock_event_msg)

        mock_callback.assert_called_once()
        self.mock_status_tracker.create_task.assert_called_once()
        self.mock_status_tracker.update_task.assert_called_with(
            event_msg=self.mock_event_msg, status=TaskStatus.COMPLETED.value
        )
        self.mock_databus.delete_message.assert_called_once_with(self.mock_event_msg)

    def test_submit_job_duplicate(self):
        """Test skipping duplicate task."""
        self.mock_status_tracker.get_task.return_value = {
            "is_duplicate": True,
            "task_details": {"status": TaskStatus.PROCESSING.value, "tracking_id": None},
        }

        mock_callback = MagicMock()
        self.job_executor.submit_job(mock_callback, self.mock_event_msg)

        mock_callback.assert_not_called()
        self.mock_status_tracker.create_task.assert_not_called()
        self.mock_status_tracker.update_task.assert_not_called()
        self.mock_databus.delete_message.assert_called_once_with(self.mock_event_msg)

    def test_submit_job_exception(self):
        """Test job submission with a callback that raises an exception."""
        expected_payload = {
            "event_name": "TEST_EVENT",
            "event_payload": {"id": "123"},
            "event_meta": {
                "trace_id": "trace-abc",
                "span_id": ANY,
                "job_id": ANY,
                "start_time": ANY,
                "end_time": ANY,
                "time_taken": ANY,
                "trigger": "MANUAL",
                "org_id": "9999",
            },
        }
        self.mock_status_tracker.get_task.return_value = None

        def failing_callback(*args, **kwargs):
            raise Exception("Something went wrong")

        self.job_executor.submit_job(failing_callback, self.mock_event_msg)

        self.mock_status_tracker.mark_task_as_failure.assert_called_once()
        self.mock_databus.publish_event.assert_called_once_with(
            "DLQ",
            expected_payload,
        )
        self.mock_databus.delete_message.assert_called_once_with(self.mock_event_msg)

    def test_check_and_update_task_status_new_task(self):
        self.mock_status_tracker.get_task.return_value = None

        is_duplicate, tracking_id = self.job_executor._check_and_update_task_status(
            self.mock_event_msg
        )

        self.assertFalse(is_duplicate)
        self.assertIsNone(tracking_id)
        self.mock_status_tracker.create_task.assert_called_once()

    def test_check_and_update_task_status_queued_task(self):
        self.mock_status_tracker.get_task.return_value = {
            "task_details": {
                "status": TaskStatus.QUEUED.value,
                "tracking_id": '{"foo": "bar"}',
            }
        }

        is_duplicate, tracking_id = self.job_executor._check_and_update_task_status(
            self.mock_event_msg
        )

        self.assertFalse(is_duplicate)
        self.assertEqual(tracking_id, {"foo": "bar"})
        self.mock_status_tracker.update_task.assert_called_once()

    def test_check_and_update_task_status_processing_task(self):
        self.mock_status_tracker.get_task.return_value = {
            "task_details": {
                "status": TaskStatus.PROCESSING.value,
                "tracking_id": '{"id": 1}',
            }
        }

        is_duplicate, tracking_id = self.job_executor._check_and_update_task_status(
            self.mock_event_msg
        )

        self.assertFalse(is_duplicate)
        self.assertEqual(tracking_id, {"id": 1})
        self.mock_status_tracker.update_task.assert_not_called()  # no update for PROCESSING


if __name__ == "__main__":
    unittest.main()
