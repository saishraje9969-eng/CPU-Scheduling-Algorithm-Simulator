"""Small built-in tests for the scheduling backend. Run: py -m unittest."""

import unittest
from scheduler import fcfs, sjf, srtf, priority_scheduling, round_robin


SAMPLE = [
    {"pid": "P1", "arrival": 0, "burst": 5, "priority": 3},
    {"pid": "P2", "arrival": 0, "burst": 3, "priority": 1},
    {"pid": "P3", "arrival": 1, "burst": 8, "priority": 4},
    {"pid": "P4", "arrival": 2, "burst": 2, "priority": 2},
]


class SchedulerTests(unittest.TestCase):
    def assert_each_process_completes_once(self, result):
        rows = result["processes"]
        self.assertEqual(len(rows), len(SAMPLE))
        self.assertEqual({r["pid"] for r in rows}, {p["pid"] for p in SAMPLE})
        self.assertTrue(all(r["completion"] >= r["arrival"] + r["burst"] for r in rows))
        self.assertTrue(all(r["waiting"] >= 0 for r in rows))

    def test_all_algorithms_finish(self):
        for result in (
            fcfs(SAMPLE), sjf(SAMPLE), srtf(SAMPLE),
            priority_scheduling(SAMPLE), round_robin(SAMPLE, 2)
        ):
            with self.subTest(algorithm=result["algorithm"]):
                self.assert_each_process_completes_once(result)

    def test_fcfs_waiting_average_for_all_arrive_at_zero(self):
        data = [
            {"pid": "A", "arrival": 0, "burst": 5, "priority": 1},
            {"pid": "B", "arrival": 0, "burst": 3, "priority": 2},
        ]
        result = fcfs(data)
        self.assertEqual([r["waiting"] for r in result["processes"]], [0, 5])
        self.assertAlmostEqual(result["metrics"]["average_waiting"], 2.5)

    def test_invalid_quantum(self):
        with self.assertRaises(ValueError):
            round_robin(SAMPLE, 0)

    def test_empty_input(self):
        with self.assertRaises(ValueError):
            fcfs([])


if __name__ == "__main__":
    unittest.main()
