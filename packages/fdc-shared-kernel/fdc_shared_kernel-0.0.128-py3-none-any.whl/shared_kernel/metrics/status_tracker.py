from collections import defaultdict
from typing import Dict


class StatsTracker:
    def __init__(self) -> None:
        # Dictionary to keep track of stats
        self._stats_counts: Dict[int, int] = defaultdict(int)

    def increment_stats_count(self, key: int) -> None:
        """Increment the count for a specific stat."""
        self._stats_counts[key] += 1

    def get_stats_counts(self) -> Dict[int, int]:
        """Return a dictionary of stats counts."""
        return dict(self._stats_counts)
