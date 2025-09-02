import re
import uuid

BinaryBlob_V1_0_1 = str | uuid.UUID | None


def is_binary_blob_v1_0_1(value):
    if isinstance(value, str) and re.match(r"^[0-9A-Fa-f]{64}$", value):
        # File hash. This is preferred over unique identifier.
        return True
    if isinstance(value, uuid.UUID):
        # Unique identifier.
        return True
    if value is None:
        # no binary data
        return True
    return False
