"""hash_batch_sync.py
Content-addressable batch exchange backend.

This implementation fills in the missing pieces of *HashBatchSync* so it can be
used as a drop‑in component for your GA or worker processes.

Key features
------------
*   **Deterministic sharded directories** based on SHA‑256 of the buffer payload.
*   Thread‑safe public API (all mutating methods behind an *RLock*).
*   **Crash tolerant**: processed batch IDs are persisted to *seen.json*.
*   Optional pruning of old batches via *max_retained*.
*   Minimal external dependencies – only `Partition` from your own code base.

Usage example
-------------
```python
sync = HashBatchSync(shared_dir="/path/to/shared", max_buffer=2048)

sync.append(obj1)
sync.append(obj2)
...
# Flush manually if auto_publish=False
sync.flush()

# Consumer side
for batch_id, payload in sync.get_batch():
    ...
```
"""

from __future__ import annotations

import json
import hashlib
import pickle
import shutil
import time
import os
from pathlib import Path
from threading import RLock
from sage_lib.partition.Partition import Partition
from ezga.core.interfaces import IAgent

from typing import Any, Dict, Generator, List, Optional, Sequence, Tuple

class Agentic_Sync(IAgent):
    """Batch‑exchange backend with *content‑addressed folders*.
    
    Parameters
    ----------
    shared_dir : str | Path
        Root directory on a shared filesystem where batches will be written.
    shard_width : int, default=2
        Number of leading hex digits of the digest used as sharding sub‑folder.
    max_buffer : int, default=8
        Flush automatically once this many objects have been appended.
    max_retained : int, optional
        Keep at most this many batch folders on disk (oldest are deleted).
        ``None`` disables pruning.
    persist_seen : bool, default=True
        Persist the *seen* index (``seen.json``) so a crash/restart does not
        re‑process the same batches.
    poll_interval : float, default=2.0
        Seconds between polls inside :meth:`watch` (exposed for future use).
    auto_publish : bool, default=True
        If *True*, :meth:`append` flushes automatically once ``max_buffer`` is
        reached.
    hash_name : str, default="sha256"
        Digest algorithm recognised by :pymod:`hashlib`.
    """

    _SEEN_FILE = "seen.json"

    # ------------------------------------------------------------
    # Construction helpers
    # ------------------------------------------------------------
    def __init__(
        self,
        *,
        shared_dir: str | Path,
        shard_width: int = 2,
        max_buffer: int = 4,
        max_retained: Optional[int] = None,
        persist_seen: bool = True,
        poll_interval: float = 2.0,
        auto_publish: bool = True,
        hash_name: str = "sha256",
        fetch_every: int = 5,
    ) -> None:

        # ── 1. root directory (try–convert) ───────────────────────────────────
        try:
            self.root = Path(shared_dir).expanduser().resolve()
            self.root.mkdir(parents=True, exist_ok=True)
        except (TypeError, AttributeError, OSError):
            # Any failure ⇒ disable backend (is_active → False)
            self.root = None

        # ── 2. hash-algorithm resolver / aliases ──────────────────────────────
        alias = {"hash": "sha256", "sha": "sha256", "sha256": "sha256", "md5": "md5"}
        algo  = alias.get(hash_name.lower().strip(), hash_name.lower().strip())
        if algo not in hashlib.algorithms_available:
            raise ValueError(
                f"Unsupported hash algorithm '{hash_name}'. "
                f"Available: {', '.join(sorted(hashlib.algorithms_available))}"
            )
        self._hash_name = algo

        # ── 3. misc configuration ─────────────────────────────────────────────
        self.shard_width = max(0, shard_width)
        self._hash_name = hash_name
        self._max_buffer = max(1, max_buffer)
        self._max_retained = max_retained
        self.poll_interval = poll_interval
        self.auto_publish = auto_publish

        self._fetch_counter = 0
        self._fetch_every = max(1, max_buffer)

        self._buffer: List[Any] = []
        self._lock = RLock()

        # ── 4. seen-index handling ────────────────────────────────────────────
        self._persist_seen = persist_seen
        self._seen_path    = self.root / self._SEEN_FILE if self.root else None
        self._seen: Dict[str, int] = self._load_seen() if self._seen_path else {}


        # Time‑tracking for watch()/append()
        self._last_flush = time.monotonic()

    # ------------------------------------------------------------
    # Runtime status helpers
    # ------------------------------------------------------------
    def is_active(self) -> bool:  # noqa: D401 – keep simple name
        """Return ``True`` when the backend is ready to use.

        The check is simple and fast – we confirm that the *root* directory
        exists **and** is writable.  External components can therefore call
        either :meth:`is_active` or its alias :meth:`active` as a lightweight
        guard before interacting with the instance.
        """
        return (
            self.root is not None
            and self.root.is_dir()
            and os.access(self.root, os.W_OK)
        )

    # Backward‑compatibility alias
    active = is_active

    # ------------------------------------------------------------
    # Public helpers
    # ------------------------------------------------------------
    def append(self, obj: Any) -> bool:
        """Stage *obj* into the in‑memory buffer.

        Returns ``True`` if the call triggered an automatic flush.
        """
        with self._lock:
            if isinstance(obj, list):
                self._buffer.extend(obj)
            else:
                self._buffer.append(obj)

            auto = False
            if self.auto_publish and len(self._buffer) >= self._max_buffer:
                self.flush()
                auto = True
            return auto

    def flush(self) -> str | None:
        """Write the current buffer to disk (if not empty) and reset state.

        Returns the *batch id* (digest string) that was written, or ``None`` when
        there was nothing to flush.
        """
        with self._lock:
            if not self._buffer:
                return None

            batch_id = self._publish_generation(self._buffer)
            self._buffer.clear()
            self._last_flush = time.monotonic()
            return batch_id

    def get_batch(
        self,
        *,
        prune: bool = True,
        sleep: float | None = None,
    ) -> Generator[Tuple[str, Any], None, None]:
        """Yield *unseen* batches (id, payload) one by one.

        Parameters
        ----------
        prune : bool, default=True
            Prune old batch folders according to *max_retained* immediately after
            loading a new batch.
        sleep : float | None
            Optional time.sleep between iterations – useful in a polling loop.
        """

        # --- Throttle scans --------------------------------------------------
        self._fetch_counter = (self._fetch_counter + 1) % self._fetch_every
        if self._fetch_counter:
            if sleep is not None:
                time.sleep(sleep)
            return  # empty generator (no scan this turn)

        while True:

            for batch_path in self._discover_batches():
                batch_id = batch_path.name
                if batch_id in self._seen:
                    continue

                try:
                    payload = self._read_partition(batch_path)
                except FileNotFoundError:
                    # Directory vanished between discovery and read → skip silently
                    continue
                except Exception as exc:
                    # Optional: log and continue, in case Partition raises something else
                    print("[HashBatchSync] read failed:", exc)
                    continue

                self._seen[batch_id] = int(time.time())
                self._save_seen()
                yield batch_id, payload

            # --- Prune once per scan ---------------------------------------
            if prune:
                self._prune_old()

            if sleep is None:
                break
            time.sleep(sleep)

    def update_behaviour(
        self,
        *,
        population: list = None,
        ctx: object = None,
    ) -> bool:
        """
        """
        return True

    # ------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------
    def _publish_generation(self, buffer: List[Any]) -> str:
        """Write *buffer* to a newly created sharded directory."""
        digest = self._hash_object_list(buffer)
        shard = digest[: self.shard_width] if self.shard_width else ""
        batch_dir = self.root / shard / digest

        if not batch_dir.exists():
            batch_dir.mkdir(parents=True, exist_ok=True)
            part = Partition()
            part.add_container(buffer)
            part.export_files(
                file_location=str(batch_dir),
                source="xyz",
                label="enumerate",
                verbose=False,
            )
        if digest not in self._seen:
            self._seen[digest] = int(time.time())
            self._save_seen()
        return digest

    def _discover_batches(self) -> List[Path]:
        """Return existing batch folders, sorted by mtime (oldest → newest).
        Directories that disappear during the scan are ignored to prevent
        FileNotFoundError races with concurrent pruning or external processes.
        """
        candidates: list[tuple[float, Path]] = []

        for path in self.root.rglob("*"):
            # Heuristic: final path component is a 64-hex SHA-256 digest.
            if len(path.parts[-1]) == 64 and path.is_dir():
                try:
                    mtime = path.stat().st_mtime        # may raise FileNotFoundError
                except FileNotFoundError:
                    continue                            # vanished between rglob and stat
                candidates.append((mtime, path))

        candidates.sort(key=lambda t: t[0])             # ascending mtime
        return [p for _, p in candidates]

    def _read_partition(self, batch_path: Path) -> Any:
        """Load data from *batch_path* via Partition.read_files."""
        part = Partition()
        part.read_files(
            file_location=os.path.join(batch_path, "config.xyz"),
            source="xyz",
            verbose=False,
        )
        return part  # You may want to return part.containers[0] or similar

    # ---------------- Seen‑index persistence --------------------
    def _load_seen(self) -> Dict[str, int]:
        if not self._persist_seen or not self._seen_path.exists():
            return {}
        try:
            return json.loads(self._seen_path.read_text())
        except Exception:
            return {}

    def _save_seen(self) -> None:
        if not self._persist_seen:
            return

        tmp = self._seen_path.with_suffix(".tmp")
        try:
            tmp.write_text(json.dumps(self._seen, indent=2))
            tmp.replace(self._seen_path)
        except OSError as exc:
            # Log but do not crash—seen index will be retried next call.
            print("[HashBatchSync] failed to write seen.json:", exc)

    # ---------------- House‑keeping helpers ---------------------
    # ---------------- Shard‑aware pruning -----------------------
    def _prune_old(self) -> None:
        """Delete *excess* oldest batches, **max one per shard** per cycle.

        This keeps I/O balanced across shard sub‑directories and eliminates the
        possibility of wiping an entire shard in one go.
        """
        if self._max_retained is None:
            return

        all_batches = self._discover_batches()  # already sorted by mtime
        excess = len(all_batches) - self._max_retained
        if excess < 1:
            return

        to_delete: List[Path] = []
        visited_shards: set[Path] = set()
        for path in all_batches:
            shard = path.parent
            if shard in visited_shards:
                continue  # already selected one from this shard this round
            to_delete.append(path)
            visited_shards.add(shard)
            if len(to_delete) == excess:
                break

        for path in to_delete:
            try:
                shutil.rmtree(path, ignore_errors=True)
            except FileNotFoundError:
                # Already gone – benign.
                continue
            except Exception as exc:
                print("[HashBatchSync] prune failed:", exc)
                continue

            # House‑keeping after successful delete
            self._seen.pop(path.name, None)
            parent = path.parent
            if parent != self.root:
                try:
                    parent.rmdir()          # deletes only if shard is empty
                except OSError:
                    # ENOENT, ENOTEMPTY, or any other benign OS error
                    # can be ignored safely
                    pass

    # ---------------- Static utilities --------------------------
    def _hash_object_list(self, objs: Sequence[object]) -> str:
        payload = pickle.dumps(objs, protocol=4)
        digest = hashlib.new(self._hash_name)
        digest.update(payload)
        return digest.hexdigest()
