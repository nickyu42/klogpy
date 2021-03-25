import pickle
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional

from src import __version__
from src.syntax import Record

CONFIG_DIR = Path.home() / '.klogger'
KLOG_FILE = CONFIG_DIR / 'time.klog'
RECORD_STORE = CONFIG_DIR / 'entries.pickle'


@dataclass
class RecordStore:
    VERSION = __version__
    _records: list[Record] = field(default_factory=list)

    # TODO: sensible value on init
    _current_record_index: int = field(default=0)

    @property
    def current_record(self) -> Optional[Record]:
        return self._records[self._current_record_index]

    def store_pending(self):
        with RECORD_STORE.open('wb') as f:
            pickle.dump(self, f)

    def push_record(self) -> Record:
        with KLOG_FILE.open('a') as f:
            current_record = self._records[self._current_record_index]
            f.write(current_record.serialize())
            f.write('\n')

            return current_record


def get_local_config(should_create: bool = False) -> tuple[bool, Optional[RecordStore]]:
    created = False
    entry_store = None

    if not CONFIG_DIR.exists() and should_create:
        CONFIG_DIR.mkdir()
        RECORD_STORE.touch()
        KLOG_FILE.touch()

        # TODO: don't create default record
        records = [Record(datetime.today())]
        entry_store = RecordStore(records)

        with RECORD_STORE.open('wb') as f:
            pickle.dump(entry_store, f)

        created = True
    elif CONFIG_DIR.exists():
        with RECORD_STORE.open('rb') as f:
            entry_store = pickle.load(f)

    return created, entry_store
