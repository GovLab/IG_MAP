from base import *
import json
import timeit

#DB
graphenedb_url = os.environ.get("GRAPHENEDB_URL", "http://localhost:7474/")
service_root = neo4j.ServiceRoot(URI(graphenedb_url).resolve("/"))
graph_db = service_root.graph_db


class MainHandler(BaseHandler):
    def get(self, display=None):
        if 'GOOGLEANALYTICSID' in os.environ:
            google_analytics_id = os.environ['GOOGLEANALYTICSID']
        else:
            google_analytics_id = False
        #----------------------------------QUERY
        tic = timeit.default_timer()
        if self.get_argument("display", None) == 'all':
            query_string = "START r=rel(*) RETURN r"
        else:
            query_string = """MATCH (n)-[r:ADDRESSES]->(m) 
                            WHERE n.type=\"Actor\" AND m.name=\"Child Pornography\" 
                            RETURN r, n.node_id, n.name, n.type, n.description, m.node_id, m.name, m.type, m.description"""
        query = neo4j.CypherQuery(graph_db, query_string)
        results = query.execute().data
        toc = timeit.default_timer()
        query_time = toc - tic
        #----------------------------------NODES
        tic = timeit.default_timer()
        nodes_unsorted = []
        links = []
        for r in results:
            nodes_unsorted.append({
                        "node":int(r.values[1]),
                        "name":str(r.values[2].encode('ascii', "ignore")).strip(),
                        "group":str(r.values[3].encode('ascii', "ignore")).strip(),
                        "description":str(r.values[4].encode('ascii', "ignore")).strip()})
            if len(r.values) > 4:
                nodes_unsorted.append({
                            "node":int(r.values[5]),
                            "name":str(r.values[6].encode('ascii', "ignore")).strip(),
                            "group":str(r.values[7].encode('ascii', "ignore")).strip(),
                            "description":str(r.values[8].encode('ascii', "ignore")).strip()})
            links.append({"source":int(r.values[1]), "target":int(r.values[5])})
        nodes = [dict(t) for t in set([tuple(d.items()) for d in nodes_unsorted])]
        logging.info(len(nodes))
        toc = timeit.default_timer()
        node_sort_time = toc - tic
        logging.info("Query time: " + str(query_time))
        logging.info("Node sort time: " + str(node_sort_time))
        self.render(
            "index.html",
            page_title='Internet Governance Map',
            page_heading='Map of Internet Governance',
            nodes=json.dumps(nodes),
            links =json.dumps(links),
            google_analytics_id=google_analytics_id,
        )
    def post(self):
        query_string = self.get_argument("query", None)
        query_string = self.application.query_builder.build(query_string)
        query = neo4j.CypherQuery(graph_db, query_string)
        results = query.execute().data
        start = set([r[0].start_node for r in results])
        end = set([r[0].end_node for r in results])
        nodes_to_keep = list(start.union(end))
        nodes = []
        for n in nodes_to_keep:
            nodes.append({
                "name":n['name'].encode('utf-8'), 
                "group":n['type'].encode('utf-8'), 
                "description":n['description'].encode('utf-8'), 
                "node":int(n['node_id'])})
        #links
        links = []
        for r in results:
            links.append({"source":int(r[0].start_node['node_id']), "target":int(r[0].end_node['node_id'])})
        self.write({"nodes":nodes, "links":links, "query":query_string})



class LoadHandler(BaseHandler):
    def get(self):
        graph_db.clear()
        node_file_path = "static/files/nodes.csv"
        relationship_file_path = "static/files/relationships.csv"
        self.application.data.load_nodes_from_file(node_file_path)
        self.application.data.load_relationships_from_file(relationship_file_path, node_file_path)
        self.write("success")
