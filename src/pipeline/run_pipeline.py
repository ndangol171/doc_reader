
from __future__ import annotations
from pathlib import Path
from ingestion.download import download_all, sha256_file, PDFS
from ingestion.parse_pdf import parse_pdf
from processing.chunk import make_chunks
from processing.embeddings import embed_texts
from extraction.indicators import extract_indicators, normalize_domain
from storage.postgres import get_engine, upsert_document, insert_chunk, upsert_indicator, insert_mention
from storage.vectorstore import ensure_collection, upsert_points
from storage.neo4j import get_driver, upsert_indicator_node, upsert_document_node, relate_mentioned_in, upsert_campaign_node, relate_part_of_campaign
from utils.text import detect_lang


DOCS = {title: url for title, url in PDFS}
CAMPAIGN_TAGS = {
    "Operation Overload": "Operation Overload",
    "Storm-1516 Technical Report": "Storm-1516",
    "Doppelgänger Campaign Report": "Doppelgänger"
}


def main():
    data_dir = Path('/tmp/docintel')
    paths = download_all(data_dir)

    engine = get_engine()
    ensure_collection()

    drv = get_driver()

    for p in paths:
        title = p.stem.replace('_', ' ')
        url = DOCS.get(title, '')
        sha = sha256_file(p)
        parsed = parse_pdf(p)
        lang = detect_lang(parsed['text'][:1000]) if parsed['text'] else 'unknown'
        doc_id = upsert_document(engine, title, url, lang, sha)
        chunks = make_chunks(parsed['text'])
        # store chunks + embeddings
        embeds = embed_texts(chunks)
        payloads = []
        chunk_ids = []
        for i, ch in enumerate(chunks):
            cid = insert_chunk(engine, doc_id, i, ch, lang)
            chunk_ids.append(cid)
            payloads.append({"doc_id": doc_id, "chunk_id": cid, "lang": lang, "campaign": CAMPAIGN_TAGS.get(title)})
        upsert_points(embeds, payloads)

        # Extract indicators from each chunk
        with drv.session() as sess:
            sess.execute_write(upsert_document_node, title, url)
            camp = CAMPAIGN_TAGS.get(title)
            if camp:
                sess.execute_write(upsert_campaign_node, camp)

        for i, ch in enumerate(chunks):
            indicators = extract_indicators(ch)
            # Domains normalized
            for (val, conf) in indicators['domain']:
                nid = upsert_indicator(engine, 'domain', val, normalize_domain(val))
                insert_mention(engine, nid, doc_id, chunk_ids[i], ch[:3000], conf)
                with drv.session() as sess:
                    sess.execute_write(upsert_indicator_node, val, 'domain')
                    sess.execute_write(relate_mentioned_in, val, url)
                    if camp:
                        sess.execute_write(relate_part_of_campaign, val, camp)
            # URLs
            for (val, conf) in indicators['url']:
                nid = upsert_indicator(engine, 'url', val, None)
                insert_mention(engine, nid, doc_id, chunk_ids[i], ch[:3000], conf)
                with drv.session() as sess:
                    sess.execute_write(upsert_indicator_node, val, 'url')
                    sess.execute_write(relate_mentioned_in, val, url)
                    if camp:
                        sess.execute_write(relate_part_of_campaign, val, camp)
            # IPs
            for (val, conf) in indicators['ip']:
                nid = upsert_indicator(engine, 'ip', val, None)
                insert_mention(engine, nid, doc_id, chunk_ids[i], ch[:3000], conf)
                with drv.session() as sess:
                    sess.execute_write(upsert_indicator_node, val, 'ip')
                    sess.execute_write(relate_mentioned_in, val, url)
                    if camp:
                        sess.execute_write(relate_part_of_campaign, val, camp)
            # Emails
            for (val, conf) in indicators['email']:
                nid = upsert_indicator(engine, 'email', val, None)
                insert_mention(engine, nid, doc_id, chunk_ids[i], ch[:3000], conf)
                with drv.session() as sess:
                    sess.execute_write(upsert_indicator_node, val, 'email')
                    sess.execute_write(relate_mentioned_in, val, url)
                    if camp:
                        sess.execute_write(relate_part_of_campaign, val, camp)
            # Phones
            for (val, conf) in indicators['phone']:
                nid = upsert_indicator(engine, 'phone', val, None)
                insert_mention(engine, nid, doc_id, chunk_ids[i], ch[:3000], conf)
                with drv.session() as sess:
                    sess.execute_write(upsert_indicator_node, val, 'phone')
                    sess.execute_write(relate_mentioned_in, val, url)
                    if camp:
                        sess.execute_write(relate_part_of_campaign, val, camp)
            # Social
            for (val, conf) in indicators['social']:
                nid = upsert_indicator(engine, 'social', val, None)
                insert_mention(engine, nid, doc_id, chunk_ids[i], ch[:3000], conf)
                with drv.session() as sess:
                    sess.execute_write(upsert_indicator_node, val, 'social')
                    sess.execute_write(relate_mentioned_in, val, url)
                    if camp:
                        sess.execute_write(relate_part_of_campaign, val, camp)
            # Trackers
            for (val, conf) in indicators['tracker']:
                nid = upsert_indicator(engine, 'tracker', val, None)
                insert_mention(engine, nid, doc_id, chunk_ids[i], ch[:3000], conf)
                with drv.session() as sess:
                    sess.execute_write(upsert_indicator_node, val, 'tracker')
                    sess.execute_write(relate_mentioned_in, val, url)
                    if camp:
                        sess.execute_write(relate_part_of_campaign, val, camp)

    print("Ingestion completed.")


if __name__ == '__main__':
    main()
