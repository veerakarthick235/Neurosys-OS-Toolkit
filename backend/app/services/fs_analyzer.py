"""
NeuroSys OS Toolkit - File System Analyzer
Detects duplicate files, junk/temp files, and provides disk usage breakdown.
"""

import os
import hashlib
import time
import fnmatch
from typing import List, Dict
from collections import defaultdict
from app.config import settings
from app.models.schemas import (
    DuplicateGroup, DuplicateResponse, JunkFile, JunkResponse, FileSystemSummary
)


def _format_size(size_bytes: int) -> str:
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"


def _file_hash(filepath: str, chunk_size: int = 8192) -> str:
    hasher = hashlib.md5()
    try:
        with open(filepath, 'rb') as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                hasher.update(chunk)
        return hasher.hexdigest()
    except (PermissionError, OSError):
        return ""


class FileSystemAnalyzer:
    def __init__(self):
        self._scan_cache: Dict = {}
        self._files_list: List[Dict] = []

    def scan_directory(self, path: str, max_depth: int = 5) -> FileSystemSummary:
        start = time.time()
        path = os.path.abspath(path)
        if not os.path.isdir(path):
            raise ValueError(f"Path '{path}' is not a valid directory")

        self._files_list = []
        total_files = 0
        total_dirs = 0
        total_size = 0
        ext_breakdown = defaultdict(lambda: {"count": 0, "total_size": 0})

        file_count = 0
        for root, dirs, files in os.walk(path):
            depth = root.replace(path, '').count(os.sep)
            if depth >= max_depth:
                dirs.clear()
                continue
            total_dirs += len(dirs)
            for fname in files:
                if file_count >= settings.MAX_SCAN_FILES:
                    break
                filepath = os.path.join(root, fname)
                try:
                    size = os.path.getsize(filepath)
                    total_files += 1
                    total_size += size
                    file_count += 1
                    ext = os.path.splitext(fname)[1].lower() or "(no ext)"
                    ext_breakdown[ext]["count"] += 1
                    ext_breakdown[ext]["total_size"] += size
                    self._files_list.append({"path": filepath, "size": size, "name": fname})
                except (PermissionError, OSError):
                    continue

        # Format extension breakdown
        for ext in ext_breakdown:
            ext_breakdown[ext]["total_size_formatted"] = _format_size(ext_breakdown[ext]["total_size"])

        # Get largest files
        sorted_files = sorted(self._files_list, key=lambda x: x["size"], reverse=True)
        largest = [{"path": f["path"], "size": f["size"], "size_formatted": _format_size(f["size"])} for f in sorted_files[:10]]

        elapsed = (time.time() - start) * 1000
        self._scan_cache = {"path": path, "files": self._files_list}

        return FileSystemSummary(
            total_files=total_files, total_dirs=total_dirs,
            total_size_bytes=total_size, total_size_formatted=_format_size(total_size),
            largest_files=largest, extension_breakdown=dict(ext_breakdown),
            scan_path=path, scan_duration_ms=round(elapsed, 2)
        )

    def find_duplicates(self) -> DuplicateResponse:
        if not self._files_list:
            return DuplicateResponse(groups=[], total_wasted_bytes=0, total_wasted_formatted="0 B", total_duplicate_files=0)

        # Group by size first (fast filter)
        size_groups = defaultdict(list)
        for f in self._files_list:
            if f["size"] > 0:
                size_groups[f["size"]].append(f)

        # Hash only files with same size
        hash_groups = defaultdict(list)
        for size, files in size_groups.items():
            if len(files) < 2:
                continue
            for f in files:
                h = _file_hash(f["path"])
                if h:
                    hash_groups[h].append(f)

        groups = []
        total_wasted = 0
        total_dup_files = 0
        for h, files in hash_groups.items():
            if len(files) < 2:
                continue
            size = files[0]["size"]
            wasted = size * (len(files) - 1)
            total_wasted += wasted
            total_dup_files += len(files) - 1
            groups.append(DuplicateGroup(
                hash=h, size_bytes=size, size_formatted=_format_size(size),
                files=[f["path"] for f in files], wasted_bytes=wasted
            ))

        groups.sort(key=lambda g: g.wasted_bytes, reverse=True)
        return DuplicateResponse(groups=groups[:50], total_wasted_bytes=total_wasted,
            total_wasted_formatted=_format_size(total_wasted), total_duplicate_files=total_dup_files)

    def find_junk_files(self) -> JunkResponse:
        if not self._files_list:
            return JunkResponse(files=[], total_junk_bytes=0, total_junk_formatted="0 B", total_junk_files=0)

        junk = []
        total_size = 0
        for f in self._files_list:
            fname = f["name"].lower()
            for pattern in settings.JUNK_PATTERNS:
                if fnmatch.fnmatch(fname, pattern):
                    junk.append(JunkFile(
                        path=f["path"], size_bytes=f["size"],
                        size_formatted=_format_size(f["size"]),
                        reason=f"Matches junk pattern: {pattern}"
                    ))
                    total_size += f["size"]
                    break

        junk.sort(key=lambda j: j.size_bytes, reverse=True)
        return JunkResponse(files=junk[:100], total_junk_bytes=total_size,
            total_junk_formatted=_format_size(total_size), total_junk_files=len(junk))

fs_analyzer = FileSystemAnalyzer()
