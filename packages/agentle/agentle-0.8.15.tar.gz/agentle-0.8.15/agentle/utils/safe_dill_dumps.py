import io
from typing import Any
import dill


def safe_dill_dumps(obj: Any):
    """Avoid numpy array serialization bug"""

    buffer = io.BytesIO()
    pickler = dill.Pickler(buffer)
    pickler.dump(obj)
    return buffer.getvalue()
