import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app.service import list_tasks


class TaskSearchTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.data_file = Path(temporary.name) / "tasks.json"
        common = {
            "priority": "medium",
            "created_at": "2026-02-25T16:00:00+00:00",
            "completed_at": None,
        }
        tasks = [
            {
                **common,
                "id": 1,
                "title": "Launch recap",
                "description": "Internal summary",
                "status": "done",
                "completed_at": "2026-02-26T16:00:00+00:00",
            },
            {
                **common,
                "id": 2,
                "title": "Plan review",
                "description": "Discuss LAUNCH timing",
                "status": "open",
            },
            {
                **common,
                "id": 3,
                "title": "Straße audit",
                "description": "Weekly report",
                "status": "open",
            },
        ]
        self.data_file.write_text(json.dumps(tasks), encoding="utf-8")
        data_path = patch("app.store.DATA_FILE", self.data_file)
        data_path.start()
        self.addCleanup(data_path.stop)

    def test_search_matches_title_or_description_case_insensitively(self):
        for query, expected_ids in [
            ("lAuNcH", [1, 2]),
            ("ReCaP", [1]),
            ("sUMMArY", [1]),
            ("AuNc", [1, 2]),
            ("STRASSE", [3]),
            ("no match", []),
        ]:
            with self.subTest(query=query):
                self.assertEqual(
                    [task["id"] for task in list_tasks(q=query)], expected_ids
                )

    def test_search_combines_with_status(self):
        for status, expected_ids in [("open", [2]), ("done", [1])]:
            with self.subTest(status=status):
                self.assertEqual(
                    [task["id"] for task in list_tasks(status=status, q="launch")],
                    expected_ids,
                )

    def test_missing_search_preserves_existing_results(self):
        self.assertEqual([task["id"] for task in list_tasks()], [1, 2, 3])
        self.assertEqual(
            [task["id"] for task in list_tasks(status="open")], [2, 3]
        )


if __name__ == "__main__":
    unittest.main()
