from base import *
import json

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
        if self.get_argument("display", None) == 'all':
            query_string = "START r=rel(*) RETURN r"
        else:
            query_string = "MATCH (n)-[r:ADDRESSES]->(m) WHERE n.type=\"Actor\" AND m.name=\"Broadband Promotion\" RETURN DISTINCT r, n"
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
        logging.info(display)
        self.render(
            "index.html",
            page_title='Internet Governance Map',
            page_heading='Map of Internet Governance',
            nodes=nodes,
            links =links,
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
