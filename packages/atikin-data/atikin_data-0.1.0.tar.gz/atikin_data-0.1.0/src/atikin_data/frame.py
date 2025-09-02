from typing import List, Dict, Any, Optional
import math
import statistics


class AtikinDataFrame:
    """
    Very small DataFrame-like object backed by a list of dicts.
    Designed for small-to-medium data and as a lightweight pandas alternative.
    """

    def __init__(self, data: Optional[List[Dict[str, Any]]] = None):
        self._data = data or []
        self.columns = list(self._data[0].keys()) if self._data else []

    def __repr__(self):
        rows_preview = min(5, len(self._data))
        return f"<AtikinDataFrame rows={len(self._data)} cols={len(self.columns)}>"

    @property
    def shape(self):
        return (len(self._data), len(self.columns))

    def head(self, n: int = 5):
        return AtikinDataFrame(self._data[:n])

    def tail(self, n: int = 5):
        return AtikinDataFrame(self._data[-n:])

    def to_dict(self) -> List[Dict[str, Any]]:
        return self._data

    def to_list_of_lists(self):
        return [[row.get(col, None) for col in self.columns] for row in self._data]

    def _col_values(self, col: str):
        vals = [row.get(col) for row in self._data]
        return vals

    def describe(self):
        """
        Return a simple statistical summary for numeric columns.
        Output: dict {column: {count, mean, std, min, 25%, 50%, 75%, max}}
        """
        summary = {}
        for col in self.columns:
            raw = self._col_values(col)
            # keep only convertible-to-float values
            nums = []
            for v in raw:
                if v is None:
                    continue
                try:
                    num = float(v)
                    if math.isfinite(num):
                        nums.append(num)
                except Exception:
                    continue
            if not nums:
                continue
            nums_sorted = sorted(nums)
            cnt = len(nums_sorted)
            mean = statistics.mean(nums_sorted)
            std = statistics.stdev(nums_sorted) if cnt > 1 else 0.0
            mn = nums_sorted[0]
            mx = nums_sorted[-1]

            def _percentile(arr, p):
                if not arr:
                    return None
                k = (len(arr) - 1) * (p / 100.0)
                f = math.floor(k)
                c = math.ceil(k)
                if f == c:
                    return arr[int(k)]
                d = k - f
                return arr[f] + d * (arr[c] - arr[f])

            summary[col] = {
                "count": cnt,
                "mean": mean,
                "std": std,
                "min": mn,
                "25%": _percentile(nums_sorted, 25),
                "50%": _percentile(nums_sorted, 50),
                "75%": _percentile(nums_sorted, 75),
                "max": mx,
            }
        return summary
