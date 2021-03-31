import pickle
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from klogpy import __version__
from klogpy.syntax import Record

CONFIG_DIR = Path.home() / '.klogger'
KLOG_FILE = CONFIG_DIR / 'time.klog'
RECORD_STORE = CONFIG_DIR / 'records.pickle'


@dataclass
class RecordStore:
    VERSION = __version__
    records: list[Record] = field(default_factory=list)

    # TODO: sensible value on init
    current_record_index: Optional[int] = field(default=None)

    @property
    def current_record(self) -> Optional[Record]:
        if self.current_record_index is None:
            return None

        return self.records[self.current_record_index]

    def commit(self):
        """Add changes to this object, to the record store. """
        with RECORD_STORE.open('wb') as f:
            pickle.dump(self, f)

    def write_selected(self) -> Record:
        """
        Write the currently selected record to the Klog file.

        :return: The written record.
        """
        current_record = self.current_record
        if current_record is None:
            raise ValueError('The current record store is empty')

        with KLOG_FILE.open('a') as f:
            f.write(current_record.serialize())
            f.write('\n')

        return current_record

    def push_record(self, record: Record):
        self.records.append(record)

        if self.current_record_index is None:
            self.current_record_index = 0
            return

        self.current_record_index += 1

    def pop_record(self, index: int):
        if index < 0 or index >= len(self.records):
            raise IndexError(f'There is no record at index {index}')

        self.records.pop(index)

        if len(self.records) == 0:
            self.current_record_index = None
        else:
            self.current_record_index -= 1


def get_local_config(should_create: bool = False) -> tuple[bool, Optional[RecordStore]]:
    created = False
    entry_store = None

    if not CONFIG_DIR.exists() and should_create:
        CONFIG_DIR.mkdir()
        RECORD_STORE.touch()
        KLOG_FILE.touch()
        entry_store = RecordStore()

        with RECORD_STORE.open('wb') as f:
            pickle.dump(entry_store, f)

        created = True
    elif CONFIG_DIR.exists() and RECORD_STORE.exists():
        with RECORD_STORE.open('rb') as f:
            entry_store = pickle.load(f)

    return created, entry_store
