from .__version__ import __version__

import os
import shutil
import hashlib
from datetime import datetime
from typing import Tuple, Any

def hash_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()

def compare_files(src_file: str, dst_file: str, method: str = "exists") -> Tuple[bool, str, Any, Any]:
    """
    Compare src_file with dst_file based on method.

    Returns:
        is_diff (bool): True if files differ
        reason (str): description of difference
        src_val (Any): relevant value from src file (size, mtime, hash prefix, or '-')
        dst_val (Any): relevant value from dst file (size, mtime, hash prefix, or '-')
    """
    if not os.path.exists(dst_file):
        return True, "missing", "-", "-"
    
    if method == "exists":
        return False, "", "-", "-"
    elif method == "mtime":
        src_mtime = os.path.getmtime(src_file)
        dst_mtime = os.path.getmtime(dst_file)
        if src_mtime != dst_mtime:
            return True, "mtime differs", datetime.fromtimestamp(src_mtime), datetime.fromtimestamp(dst_mtime)
    elif method == "size":
        src_size = os.path.getsize(src_file)
        dst_size = os.path.getsize(dst_file)
        if src_size != dst_size:
            return True, "size differs", src_size, dst_size
    elif method == "hash":
        src_hash = hash_file(src_file)
        dst_hash = hash_file(dst_file)
        if src_hash != dst_hash:
            return True, "hash differs", src_hash[:8], dst_hash[:8]
    
    return False, "", "-", "-"
