# tag_revolution_prototype_v2.py
"""
Tag Revolution: multi-layer semantic + temporal coordinate prototype
-------------------------------------------------------------------
This is a pure-Python, dependency-free proof-of-concept demonstrating:
  • Multi-layer semantic coordinates (surface / conceptual / relational stubs)
  • Multi-scale temporal encoding (absolute / relative / periodic / era bucket)
  • Query expansion from partial memory ("memory cues")
  • Retrieval returning: ranked list + timeline + semantic_map (node/edge view)
NOTE: All ML components are lightweight stubs for demonstration purposes.
      Replace stub functions with real models in production.

License: Contract Tag CT-IDA-001 (refer to Zenodo record).
"""

from __future__ import annotations
import math, time, json, hashlib, datetime
from dataclasses import dataclass, field
from typing import List, Dict, Any, Tuple

# ------------------------- Utilities -------------------------

def _hash_to_unit_vec(s: str, dim: int = 64) -> list[float]:
    """Deterministic pseudo-embedding via hashing into a fixed dimension.
    Not meaningful semantically; used for structure demonstration only.
    """
    v = [0.0]*dim
    for i, ch in enumerate(s.encode('utf-8')):
        idx = (ch + i) % dim
        v[idx] += 1.0
    # L2 normalize
    norm = math.sqrt(sum(x*x for x in v)) or 1.0
    return [x/norm for x in v]

def _cosine(a: List[float], b: List[float]) -> float:
    num = sum(x*y for x,y in zip(a,b))
    da = math.sqrt(sum(x*x for x in a)) or 1.0
    db = math.sqrt(sum(y*y for y in b)) or 1.0
    return num / (da*db)

def _concat(*vecs: List[float]) -> List[float]:
    out = []
    for v in vecs:
        out.extend(v)
    return out

# ------------------------- Semantic layers (stubs) -------------------------

def embed_surface(text: str, dim: int = 64) -> List[float]:
    """Surface-level embedding (bag-of-chars hashed)."""
    return _hash_to_unit_vec(text.lower(), dim)

_CONCEPT_LEXICON = {
    # toy concept hints; expand in production
    "contract": ["license","agreement","permission","auth"],
    "tag": ["label","marker","token"],
    "search": ["retrieve","lookup","find"],
    "temporal": ["time","timeline","era","period"],
    "semantic": ["meaning","synonym","concept","context"],
}

def embed_concepts(text: str, dim: int = 32) -> List[float]:
    """Conceptual embedding via lexicon hits → hashed into vector space."""
    hits = []
    low = text.lower()
    for key, syns in _CONCEPT_LEXICON.items():
        if key in low or any(s in low for s in syns):
            hits.append(key)
    if not hits:
        hits = ["other"]
    sig = "|".join(sorted(hits))
    return _hash_to_unit_vec(sig, dim)

def extract_relations(text: str) -> Dict[str, float]:
    """Very small relational cue extractor (counts co-occurrence of key pairs)."""
    pairs = [("contract","tag"), ("semantic","temporal"), ("search","map")]
    low = text.lower()
    feats = {}
    for a,b in pairs:
        c = 1.0 if (a in low and b in low) else 0.0
        if c:
            feats[f"rel:{a}-{b}"] = c
    return feats

def embed_relational(feats: Dict[str,float], dim: int = 16) -> List[float]:
    """Hash sparse relation features into a dense vector."""
    if not feats:
        return [0.0]*dim
    sig = "|".join(sorted(feats.keys()))
    return _hash_to_unit_vec(sig, dim)

# ------------------------- Temporal layers -------------------------

def encode_timestamp(ts: float, dim: int = 16) -> List[float]:
    """Absolute time encoding via sinusoidal features."""
    # scale to days
    days = ts / 86400.0
    v = []
    for k in range(dim//2):
        freq = 1.0 / (2.0**k)
        v.append(math.sin(days*freq))
        v.append(math.cos(days*freq))
    return v

def encode_time_delta(ts: float, ref_ts: float | None = None, dim: int = 8) -> List[float]:
    """Relative delta to reference time (now if None)."""
    ref = ref_ts if ref_ts is not None else time.time()
    delta_days = (ref - ts) / 86400.0
    # Signed, with tanh squash
    x = math.tanh(delta_days / 30.0)  # ~month scale
    return [x]*(dim)

def encode_periodic(ts: float, dim: int = 8) -> List[float]:
    """Weekly/monthly periodic signals."""
    dt = datetime.datetime.utcfromtimestamp(ts)
    dow = dt.weekday() / 6.0 * 2*math.pi  # 0..6 → 0..2π
    moy = (dt.month-1)/11.0 * 2*math.pi  # 1..12 → 0..2π
    return [math.sin(dow), math.cos(dow), math.sin(moy), math.cos(moy)] + [0.0]*(dim-4)

def encode_era_context(ts: float, dim: int = 4) -> List[float]:
    """Era bucket (toy): pre-2020, 2020-2022, 2023-2024, 2025+."""
    year = datetime.datetime.utcfromtimestamp(ts).year
    if year < 2020:
        idx = 0
    elif year <= 2022:
        idx = 1
    elif year <= 2024:
        idx = 2
    else:
        idx = 3
    v = [0.0]*dim
    v[idx] = 1.0
    return v

# ------------------------- Memory reconstruction -------------------------

_SYNONYM_HINTS = {
    "search": ["lookup","retrieve","find","query"],
    "map": ["graph","network","topology"],
    "temporal": ["time","chrono","timeline","when"],
    "semantic": ["meaning","context","synonym","concept"],
    "contract": ["license","agreement","permission","auth"],
}

def expand_partial_memory(query: str, user_memory: Dict[str,Any] | None = None) -> str:
    """Expand short/fragmentary query by appending synonym hints inferred from tokens."""
    toks = query.lower().split()
    extra = []
    for t in toks:
        for k, syns in _SYNONYM_HINTS.items():
            if t==k or t in syns:
                extra.extend([s for s in syns if s not in toks])
    # incorporate user memory cues if provided
    if user_memory and isinstance(user_memory.get("cues"), list):
        extra.extend([c for c in user_memory["cues"] if c not in toks])
    if extra:
        return query + " " + " ".join(sorted(set(extra)))
    return query

# ------------------------- Data structures -------------------------

@dataclass
class TagItem:
    id: str
    content: str
    timestamp: float
    meta: Dict[str,Any] = field(default_factory=dict)
    vec: List[float] = field(default_factory=list)

class TagDB:
    def __init__(self):
        self.items: List[TagItem] = []

    def add(self, item: TagItem):
        item.vec = self.vectorize(item.content, item.timestamp)
        self.items.append(item)

    # Core vectorization (multi-layer)
    def vectorize(self, content: str, ts: float) -> List[float]:
        # semantic layers
        v_surface = embed_surface(content, 64)
        v_concept = embed_concepts(content, 32)
        v_rel = embed_relational(extract_relations(content), 16)
        # temporal layers
        v_abs = encode_timestamp(ts, 16)
        v_rel_delta = encode_time_delta(ts, None, 8)
        v_period = encode_periodic(ts, 8)
        v_era = encode_era_context(ts, 4)
        return _concat(v_surface, v_concept, v_rel, v_abs, v_rel_delta, v_period, v_era)

    def search(self, query: str, user_memory: Dict[str,Any] | None = None, topk: int = 5) -> Dict[str,Any]:
        q = expand_partial_memory(query, user_memory)
        q_vec = self.vectorize(q, time.time())
        scored = []
        for it in self.items:
            s = _cosine(q_vec, it.vec)
            scored.append((s, it))
        scored.sort(key=lambda x: x[0], reverse=True)
        top = scored[:topk]

        # Build outputs
        ranked = [{"id": it.id, "score": round(s,4), "content": it.content, "timestamp": it.timestamp, "meta": it.meta} for s,it in top]

        # timeline (sorted by timestamp of top candidates)
        timeline = sorted(ranked, key=lambda r: r["timestamp"])

        # semantic_map: nodes = ids, edges when relation cue overlaps (toy)
        nodes = [{"id": r["id"]} for r in ranked]
        edges = []
        for i in range(len(top)):
            for j in range(i+1, len(top)):
                a = extract_relations(top[i][1].content)
                b = extract_relations(top[j][1].content)
                if set(a.keys()) & set(b.keys()):
                    edges.append({"source": top[i][1].id, "target": top[j][1].id, "type": "rel-overlap"})
        semantic_map = {"nodes": nodes, "edges": edges}

        return {"expanded_query": q, "ranked_list": ranked, "timeline": timeline, "semantic_map": semantic_map}


# ------------------------- Demo usage -------------------------

def _demo():
    db = TagDB()
    now = time.time()
    samples = [
        TagItem("A", "Semantic search map with temporal layers and contract tag licensing", now - 86400*400, {"url":"https://zenodo.org/records/17447593"}),
        TagItem("B", "Timeline UI for search results with era context and memory reconstruction", now - 86400*1200, {}),
        TagItem("C", "Contract Tag required for structural coherence in meaning retrieval systems", now - 86400*100, {}),
        TagItem("D", "Synonym expansion and conceptual embedding for associative queries", now - 86400*30, {}),
        TagItem("E", "Keyword ranking baseline without temporal encoding", now - 86400*5, {}),
    ]
    for s in samples:
        db.add(s)

    res = db.search("tag revolution semantic time", user_memory={"cues":["contract","timeline"]}, topk=5)
    print(json.dumps(res, indent=2))

if __name__ == "__main__":
    _demo()
