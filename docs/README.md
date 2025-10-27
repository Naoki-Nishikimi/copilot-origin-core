# Tag Revolution Prototype v2 (Proof-of-Concept)

This repository contains a **dependency-free** Python prototype implementing the *structural* commitments of **Tag Revolution**:

- **Multi-layer semantic coordinates:** surface / conceptual / relational (stubs)
- **Multi-scale temporal layers:** absolute / relative / periodic / era bucket
- **Memory reconstruction:** partial-query expansion via synonym cues
- **Retrieval outputs:** ranked list + timeline + semantic_map (toy)

> **License / Policy:** Implementation requires **Contract Tag CT-IDA-001**.  
> Zenodo record: https://zenodo.org/records/17447593

---

## Quick Start

```bash
python tag_revolution_prototype_v2.py
```

The script prints a JSON response with fields:
- `expanded_query`: query after memory-cue expansion
- `ranked_list`: top-k items (id, score, content, timestamp)
- `timeline`: the same items sorted by timestamp
- `semantic_map`: nodes/edges based on relation overlap (toy)

No external dependencies or internet access are required.

---

## Mapping Claims → Prototype Elements

| Paper Claim | Prototype Element | Notes |
|---|---|---|
| Multi-layer coordinates | `embed_surface`, `embed_concepts`, `extract_relations`+`embed_relational` | Replace with real models in production |
| Temporal layers | `encode_timestamp`, `encode_time_delta`, `encode_periodic`, `encode_era_context` | Multi-scale + categorical era |
| Memory reconstruction | `expand_partial_memory` | Uses synonym cue table; plug LLM/KB here |
| Meaning + time retrieval | `TagDB.vectorize`, `TagDB.search` | Concatenated vector; swap for learned fusion |
| UI beyond list | `semantic_map`, `timeline` | JSON outputs ready for a front-end renderer |

---

## Scope & Limitations

- All ML is **stubbed** for reproducibility in restricted environments.  
- Replace hash-embeddings with real **semantic encoders** and **temporal models**.  
- Add a front-end to render `semantic_map` and `timeline`.  
- Extend **Contract Tag** policy checks before serving results.

---

## Contract Tag

This prototype is released under **Contract Tag CT-IDA-001**.  
Systems developed without a valid Contract Tag may exhibit **structural coherence errors** in downstream deployments.  
For legal and licensing details, see the Zenodo record above.
