# storage_backend.py
import sqlite3, pickle
from typing import Any, Dict, List, Union, Sequence
from abc import ABC, abstractmethod

StorageType = Union[List[Any], Dict[int, Any]]

class StorageBackend(ABC):
    """
    Abstract interface for container storage backends.
    """
    @abstractmethod
    def add(self, obj) -> int:
        """Store object and return its ID."""
        raise NotImplementedError("add must be implemented by subclasses")

    @abstractmethod
    def get(self, obj_id: int):
        """Retrieve object by ID."""
        raise NotImplementedError("get must be implemented by subclasses")

    @abstractmethod
    def remove(self, obj_id: int) -> None:
        """Delete object by ID."""
        raise NotImplementedError("remove must be implemented by subclasses")

    @abstractmethod
    def list_ids(self) -> List[int]:
        """Return list of all object IDs."""
        raise NotImplementedError("list_ids must be implemented by subclasses")

    @abstractmethod
    def count(self) -> int:
        """Return total number of stored objects."""
        raise NotImplementedError("count must be implemented by subclasses")

class MemoryStorage(StorageBackend):
    """
    Generic in‑memory storage.

    The container can be either a list (sequential storage) or a dict that maps
    integer IDs to objects.  All public methods behave the same for both
    back‑ends; IDs are always integers.
    """

    def __init__(self, initial: StorageType | None = None) -> None:
        # Default to an empty list if no container is supplied
        self._data: StorageType = initial if initial is not None else []

    # --------------------------------------------------------------------- #
    # Mutators
    # --------------------------------------------------------------------- #
    def add(self, obj: Any) -> int:
        """
        Store *obj* and return its integer ID.

        * list‑backend   → object is appended; ID == len(list) − 1
        * dict‑backend   → object is stored under the next free integer key
        """
        if isinstance(self._data, list):
            self._data.append(obj)
            return len(self._data) - 1
        else:  # dict
            new_id: int = max(self._data.keys(), default=-1) + 1
            self._data[new_id] = obj
            return new_id

    def set(self, container: StorageType) -> int:
        """
        Replace the entire backing store with *container* (must be list or dict).
        Returns the highest valid ID after the operation, or −1 if empty.
        """
        if not isinstance(container, (list, dict)):
            raise TypeError("container must be a list or a dict[int, Any]")
        self._data = container
        return len(self._data) - 1

    def remove(self, obj_id: int) -> None:
        """
        Delete the object with ID *obj_id*.
        Raises KeyError if the ID is invalid.
        """
        try:
            del self._data[obj_id]               # works for both list & dict
        except (IndexError, KeyError):
            raise KeyError(f"No object found with id {obj_id}") from None

    # --------------------------------------------------------------------- #
    # Accessors
    # --------------------------------------------------------------------- #
    def get(self, obj_id: int | None = None) -> Any:
        """
        Retrieve a single object by ID, or the entire container if *obj_id* is
        None.  Raises KeyError/IndexError if the ID is invalid.
        """
        if obj_id is None:
            return self._data
        try:
            return self._data[obj_id]
        except (IndexError, KeyError):
            raise KeyError(f"No object found with id {obj_id}") from None

    def list_ids(self) -> List[int]:
        """Return all valid integer IDs."""
        return list(range(len(self._data))) if isinstance(self._data, list) \
            else list(self._data.keys())

    def count(self) -> int:                     # O(1) for both back‑ends
        """Number of stored elements."""
        return len(self._data)

class MemoryStorage(StorageBackend):
    """
    In-memory storage using a Python list.
    """
    def __init__(self):
        self._data: List = []

    def add(self, obj) -> int:
        self._data.append(obj)
        return len(self._data) - 1

    def get(self, obj_id: int=None):
        try:
            if obj_id:
                return self._data[obj_id]
            else:
                return self._data

        except IndexError:
            raise KeyError(f"No object found with id {obj_id}")

    def set(self, obj_list: list):
        try:
            self._data = obj_list
            return len(self._data) - 1
        except IndexError:
            raise KeyError(f"Error in set data {obj_id}")

    def remove(self, obj_id: int) -> None:
        try:
            del self._data[obj_id]
        except IndexError:
            raise KeyError(f"No object found with id {obj_id}")

    def list_ids(self) -> List[int]:
        return list(range(len(self._data)))

    def count(self) -> int:
        return len(self._data)

class SQLiteStorage(StorageBackend):
    """
    SQLite-based storage, pickling objects into a BLOB.
    """
    def __init__(self, db_path: str):
        # ensure directory exists
        import os
        dir_path = os.path.dirname(db_path)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)

        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._init_schema()

    def _init_schema(self) -> None:
        cur = self.conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS containers (
                id   INTEGER PRIMARY KEY AUTOINCREMENT,
                data BLOB NOT NULL
            );
            """
        )
        self.conn.commit()

    def add(self, obj) -> int:
        blob = pickle.dumps(obj)
        cur = self.conn.cursor()
        cur.execute("INSERT INTO containers (data) VALUES (?);", (blob,))
        self.conn.commit()
        return cur.lastrowid

    def get(self, obj_id: int):
        cur = self.conn.cursor()
        cur.execute("SELECT data FROM containers WHERE id = ?;", (obj_id,))
        row = cur.fetchone()
        if row is None:
            raise KeyError(f"No container with id {obj_id}")
        return pickle.loads(row[0])

    def remove(self, obj_id: int) -> None:
        cur = self.conn.cursor()
        cur.execute("DELETE FROM containers WHERE id = ?;", (obj_id,))
        if cur.rowcount == 0:
            raise KeyError(f"No container with id {obj_id}")
        self.conn.commit()

    def list_ids(self) -> List[int]:
        cur = self.conn.cursor()
        cur.execute("SELECT id FROM containers;")
        return [row[0] for row in cur.fetchall()]

    def count(self) -> int:
        cur = self.conn.cursor()
        cur.execute("SELECT COUNT(*) FROM containers;")
        return cur.fetchone()[0]
