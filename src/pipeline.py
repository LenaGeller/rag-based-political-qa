
from query import normalize_query, keyword_map, build_retrieval_constraints
from ranking import apply_document_bias
from llm import prompt, model, parser
from retrieval import db

def frage_stellen(frage: str):
    # 1) Query normalisieren & Constraints bauen
    signals = normalize_query(frage, keyword_map)
    constraints = build_retrieval_constraints(signals)

    docs = []

    comparison = signals.get("comparison")
    parties = signals.get("parties", [])

    used_chunk_ids = set()

    # =========================
    # FALL: Vergleich ≥ 2 Parteien
    # =========================
    if comparison and len(parties) >= 2:

        # 1) Mindestabdeckung: 1 Chunk pro Partei
        for partei in parties:
            party_filter = {
                "$and": [
                    constraints["filters"],
                    {"partei": {"$eq": partei}}
                ]
            } if constraints["filters"] else {"partei": {"$eq": partei}}

            party_docs = db.similarity_search(
                frage,
                k=1,
                filter=party_filter
            )

            for d in party_docs:
                cid = d.metadata.get("chunk_id")
                if cid not in used_chunk_ids:
                    docs.append(d)
                    used_chunk_ids.add(cid)
        # 2) Auffüllen auf k=20 mit normalem Filter
        remaining_k = max(0, 20 - len(docs))

        if remaining_k > 0:
            extra_docs = db.similarity_search(
                frage,
                k=remaining_k,
                filter=constraints["filters"]
            )
        for d in extra_docs:
            cid = d.metadata.get("chunk_id")
            if cid not in used_chunk_ids:
                docs.append(d)
                used_chunk_ids.add(cid)

    # =========================
    # FALL: alles andere (Status quo)
    # =========================
    else:
        docs = db.similarity_search(
            frage,
            k=20,
            filter=constraints["filters"]
        )
    
    docs = apply_document_bias(docs, signals)

    # 3) Kontext bauen
    context_parts = []
    for d in docs:
        meta = d.metadata or {}
        header = (
            f"[PARTEI: {meta.get('partei','?')} | "
            f"KAPITEL: {meta.get('chapter','?')} | "
            f"JAHR: {meta.get('jahr','?')} | "
            f"QUELLE: {meta.get('source','?')}]"
        )
        context_parts.append(header + "\n" + d.page_content)

    context = "\n\n".join(context_parts)

    # 4) LLM aufrufen
    chain = prompt | model | parser


    antwort = chain.invoke({"context": context, "question": frage})

    
    return antwort, docs
