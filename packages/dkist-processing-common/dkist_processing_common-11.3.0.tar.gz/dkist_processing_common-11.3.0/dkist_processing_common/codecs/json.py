"""Encoder/decoders for writing and reading JSON files."""

import json
from pathlib import Path
from typing import Any

from dkist_processing_common.codecs.str import str_decoder
from dkist_processing_common.codecs.str import str_encoder

# Note that we could have used dump/load instead of dumps/loads but dump/load still use str under the hood and so the
# result is the same but with more steps.


def json_encoder(data: Any, encoding: str = "utf-8", errors="strict", **dumps_kwargs) -> bytes:
    """Convert data to bytes by encoding as JSON."""
    json_str = json.dumps(data, **dumps_kwargs)
    return str_encoder(json_str, encoding=encoding, errors=errors)


def json_decoder(path: Path, encoding: str = "utf-8", errors="strict", **loads_kwargs) -> Any:
    """Read a file as JSON and return the decoded objects."""
    json_str = str_decoder(path, encoding=encoding, errors=errors)
    return json.loads(json_str, **loads_kwargs)
