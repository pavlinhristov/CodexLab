import json
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

from app.service import complete_task, get_task


class CompletionPersistenceTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.data_file = Path(temporary.name) / "tasks.json"
        self.tasks = [
            {
                "id": 1,
                "title": "Finish report",
                "description": "Write the final report.",
                "status": "open",
                "priority": "medium",
                "created_at": "2026-02-25T16:00:00+00:00",
                "completed_at": None,
            },
            {
                "id": 2,
                "title": "Plan review",
                "description": "Arrange the review meeting.",
                "status": "open",
                "priority": "low",
                "created_at": "2026-02-25T16:00:00+00:00",
                "completed_at": None,
            },
        ]
        self.data_file.write_text(json.dumps(self.tasks), encoding="utf-8")
        data_path = patch("app.store.DATA_FILE", self.data_file)
        data_path.start()
        self.addCleanup(data_path.stop)

    def test_completion_persists_status_and_timestamp(self):
        completed = complete_task(1)
        fetched = get_task(1)
        stored = json.loads(self.data_file.read_text(encoding="utf-8"))

        self.assertEqual(fetched["status"], "done")
        self.assertIsNotNone(fetched["completed_at"])
        self.assertIsNotNone(datetime.fromisoformat(fetched["completed_at"]).tzinfo)
        self.assertEqual(fetched, completed)
        self.assertEqual(stored[0], fetched)
        self.assertEqual(stored[1], self.tasks[1])
        self.assertEqual(len(stored), 2)

    def test_missing_task_does_not_modify_storage(self):
        before = self.data_file.read_bytes()

        self.assertIsNone(complete_task(999))
        self.assertEqual(self.data_file.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
