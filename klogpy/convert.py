import csv
from pathlib import Path
from typing import List

from klogpy.syntax import Record


def convert_to_csv(records: List[Record], out: Path):
    with out.open('w') as f:
        writer = csv.DictWriter(f, fieldnames=('date', 'properties', 'summary', 'entries', 'tags', 'total_minutes'))
        writer.writeheader()
        writer.writerows(r.serialize_dict() for r in records)
