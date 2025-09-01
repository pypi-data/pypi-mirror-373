#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Public, ergonomic API for haste.

Facade exposing a minimal, stable interface so users can:
- select from a single file with one call (mirrors CLI behavior)
- build a repo-level payload with one call
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional
import bisect
from pathlib import Path

from .index_py import index_python_file, Symbol
from .retriever import Doc, build_bm25_corpus, lexical_topk, semantic_rerank, bfs_expand
from .cast_chunker import cast_split_merge, ByteSpan as Span
from .exporter import stitch_code

# Repo-level imports
from .scanner import iter_source_files
from .ts_utils import build_ts_parser
from .index import RepoIndex, index_python_file as ts_index_python_file
from .payload import build_llm_payload


def _to_doc_list(symbols: List[Symbol]) -> List[Doc]:
    docs: List[Doc] = []
    for i, s in enumerate(symbols):
        docs.append(Doc(
            idx=i,
            module=s.module,
            qname=s.qname,
            kind=s.kind,
            name=s.name,
            path=s.path,
            docstring=s.docstring,
            identifiers=s.identifiers,
            signature=s.signature or "",
            start_byte=s.start_byte,
            end_byte=s.end_byte,
        ))
    return docs


def _build_call_edges(symbols: List[Symbol]) -> Dict[str, List[str]]:
    edges: Dict[str, List[str]] = {}
    for s in symbols:
        out: List[str] = []
        for c in s.calls:
            base = c.split(".")[-1]
            if base not in out:
                out.append(base)
        edges[s.qname] = out
    return edges


def _build_line_starts(src_bytes: bytes) -> list[int]:
    starts = [0]
    find = src_bytes.find
    i = 0
    while True:
        j = find(b"\n", i)
        if j == -1:
            break
        starts.append(j + 1)
        i = j + 1
    return starts


def _byte_to_line(byte_off: int, line_starts: list[int]) -> int:
    return bisect.bisect_right(line_starts, byte_off)


def select_from_file(
    path: str,
    query: str,
    *,
    top_k: int = 6,
    prefilter: int = 300,
    bfs_depth: int = 1,
    max_add: int = 12,
    semantic: bool = False,
    sem_model: str = "text-embedding-3-small",
    hard_cap: int = 1200,
    soft_cap: int = 1800,
) -> Dict[str, Any]:
    if hard_cap <= 0 or soft_cap <= 0:
        raise ValueError("hard_cap and soft_cap must be positive integers")
    if soft_cap < hard_cap:
        soft_cap = hard_cap

    src_bytes, symbols, _aliases = index_python_file(path)
    docs = _to_doc_list(symbols)
    bm25, _ = build_bm25_corpus(docs)

    prelim = lexical_topk(docs, bm25, query, k=top_k, prefilter=prefilter)
    if semantic:
        prelim = semantic_rerank(prelim, query, sem_model, src_bytes=src_bytes)
    if not prelim:
        prelim = lexical_topk(docs, bm25, query, k=top_k, prefilter=max(30, top_k))

    call_edges = _build_call_edges(symbols)
    docs_by_name: Dict[str, List[Doc]] = {}
    for d in docs:
        docs_by_name.setdefault(d.name, []).append(d)
    expanded = bfs_expand(prelim[: top_k], docs_by_name, call_edges, depth=bfs_depth, max_add=max_add)

    spans = [Span(d.start_byte, d.end_byte) for d in expanded]
    stitched_spans = cast_split_merge(src_bytes, spans, hard_cap_tokens=hard_cap, soft_cap_tokens=soft_cap)
    code, _mapping = stitch_code(src_bytes, stitched_spans)

    # Nodes payload with line numbers
    nodes = []
    line_starts = _build_line_starts(src_bytes)
    for d in expanded:
        lineno = _byte_to_line(d.start_byte, line_starts)
        end_lineno = _byte_to_line(max(d.end_byte - 1, 0), line_starts)
        nodes.append({
            "type": d.kind,
            "name": d.name,
            "qname": d.qname,
            "module": d.module,
            "path": d.path,
            "lineno": lineno,
            "end_lineno": end_lineno,
            "signature": d.signature,
            "docstring": d.docstring or None,
            "score": d.score,
        })

    out = {
        "summary": {
            "total_functions": sum(1 for s in symbols if s.kind == "function"),
            "total_classes": sum(1 for s in symbols if s.kind == "class"),
        },
        "nodes": nodes,
        "classes": [n for n in nodes if n["type"] == "class"],
        "selected": {
            "roots": [d.qname for d in expanded],
            "functions": [d.qname for d in expanded if d.kind == "function"],
            "classes": [d.qname for d in expanded if d.kind == "class"],
        },
        "code": code,
    }
    return out


def build_payload_from_repo(
    root: str | Path,
    *,
    include_code: bool = False,
    top_k: int = 50,
    depth: int = 0,
    query: Optional[str] = None,
    query_weight: float = 0.5,
) -> Dict[str, Any]:
    root_path = Path(root)
    parser = build_ts_parser("python")
    idx = RepoIndex(root_path)
    for p in iter_source_files(root_path):
        ts_index_python_file(p, parser, idx)
    return build_llm_payload(
        idx,
        include_code=include_code,
        top_k=top_k,
        query=query,
        depth=depth,
        query_weight=query_weight,
    )



