# controller/jobs_helpers.py
import os
from datetime import datetime
from uuid import uuid4

EXPORT_DIR = os.path.join(os.getcwd(), "instance", "exports")
os.makedirs(EXPORT_DIR, exist_ok=True)

def write_bytes_to_exports(filename, bcontent):
    path = os.path.join(EXPORT_DIR, filename)
    with open(path, "wb") as f:
        f.write(bcontent)
    return path

def generate_filename(prefix, ext):
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    return f"{prefix}_{ts}_{uuid4().hex[:8]}.{ext}"
