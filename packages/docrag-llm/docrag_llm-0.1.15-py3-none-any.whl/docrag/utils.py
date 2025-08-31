from __future__ import annotations
import re
from typing import List

def sentence_chunks(text: str, target: int = 1000, overlap: int = 200) -> List[str]:
    text = text.strip()
    if not text:
        return []
    sentences = re.split(r'(?<=[.!?])\s+', text)
    chunks, buf, size = [], [], 0
    for s in sentences:
        L = len(s)
        if size + L + 1 > target and buf:
            chunk = " ".join(buf).strip()
            if chunk:
                chunks.append(chunk)
            tail = chunk[-overlap:] if overlap > 0 and chunk else ""
            buf = [tail, s] if tail else [s]
            size = len(tail) + L
        else:
            buf.append(s)
            size += L + 1
    if buf:
        chunk = " ".join(buf).strip()
        if chunk:
            chunks.append(chunk)
    if not chunks:
        chunks = [text[i:i + target] for i in range(0, len(text), target)]
    return chunks
