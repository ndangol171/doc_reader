
from __future__ import annotations
from neo4j import GraphDatabase
from config import settings


def get_driver():
    return GraphDatabase.driver(settings.neo4j_uri, auth=(settings.neo4j_user, settings.neo4j_password))


def upsert_indicator_node(tx, value: str, type_: str):
    tx.run("MERGE (i:Indicator {value:$v}) SET i.type=$t", v=value, t=type_)


def upsert_document_node(tx, title: str, url: str):
    tx.run("MERGE (d:Document {url:$u}) SET d.title=$t", u=url, t=title)


def upsert_campaign_node(tx, name: str):
    tx.run("MERGE (c:Campaign {name:$n})", n=name)


def relate_mentioned_in(tx, indicator_value: str, doc_url: str):
    tx.run("""
        MATCH (i:Indicator {value:$v}), (d:Document {url:$u})
        MERGE (i)-[:MENTIONED_IN]->(d)
    """, v=indicator_value, u=doc_url)


def relate_part_of_campaign(tx, indicator_value: str, campaign_name: str):
    tx.run("""
        MATCH (i:Indicator {value:$v}), (c:Campaign {name:$n})
        MERGE (i)-[:PART_OF_CAMPAIGN]->(c)
    """, v=indicator_value, n=campaign_name)


def relate_related_to(tx, src_val: str, dst_val: str, relation: str):
    tx.run("""
        MATCH (a:Indicator {value:$a}), (b:Indicator {value:$b})
        MERGE (a)-[r:RELATED_TO {type:$t}]->(b)
    """, a=src_val, b=dst_val, t=relation)


def k_hop_neighbors(indicator_value: str, k: int = 2):
    drv = get_driver()
    with drv.session() as sess:
        cypher = f"""
        MATCH (i:Indicator {{value:$v}})-[*1..{k}]-(n)
        WITH DISTINCT n
        OPTIONAL MATCH (n)-[r]-(m)
        RETURN n, r, m
        LIMIT 500
        """
        res = sess.run(cypher, v=indicator_value)
        nodes, edges = {}, []
        for rec in res:
            for node_alias in ['n', 'm']:
                node = rec.get(node_alias)
                if node is None: continue
                nid = node.element_id
                if nid not in nodes:
                    nodes[nid] = {"id": nid, "labels": list(node.labels), **dict(node)}
            r = rec.get('r')
            if r is not None:
                edges.append({"id": r.element_id, "type": r.type, "start": r.start_node.element_id, "end": r.end_node.element_id})
        return {"nodes": list(nodes.values()), "edges": edges}
