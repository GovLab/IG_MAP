from base import *
import json

#DB
graphenedb_url = os.environ.get("GRAPHENEDB_URL", "http://localhost:7474/")
service_root = neo4j.ServiceRoot(URI(graphenedb_url).resolve("/"))
graph_db = service_root.graph_db
# actor = graph_db.get_or_create_index(neo4j.Node, "Actor")
# event = graph_db.get_or_create_index(neo4j.Node, "Initiatives and Events")
# issue = graph_db.get_or_create_index(neo4j.Node, "Issue")
# law = graph_db.get_or_create_index(neo4j.Node, "Laws and Policies")
# person = graph_db.get_or_create_index(neo4j.Node, "Person")
# research = graph_db.get_or_create_index(neo4j.Node, "Research and Advocacy")
# standard = graph_db.get_or_create_index(neo4j.Node, "Standards")
# tool = graph_db.get_or_create_index(neo4j.Node, "Tools and Resources")
# addresses = graph_db.get_or_create_index(neo4j.Relationship, "ADDRESSES")
# administrates = graph_db.get_or_create_index(neo4j.Relationship, "ADMINISTRATES")
# adopted = graph_db.get_or_create_index(neo4j.Relationship, "ADOPTED")
# advises = graph_db.get_or_create_index(neo4j.Relationship, "ADVISES")
# authored = graph_db.get_or_create_index(neo4j.Relationship, "AUTHORED")
# collaborated_on = graph_db.get_or_create_index(neo4j.Relationship, "COLLABORATED_ON")
# commissioned = graph_db.get_or_create_index(neo4j.Relationship, "COMMISSIONED")
# commissioned = graph_db.get_or_create_index(neo4j.Relationship, "CONVENED")
# commissioned = graph_db.get_or_create_index(neo4j.Relationship, "COORDINATES")
# commissioned = graph_db.get_or_create_index(neo4j.Relationship, "CREATED")
# commissioned = graph_db.get_or_create_index(neo4j.Relationship, "DEVELOPED")
# commissioned = graph_db.get_or_create_index(neo4j.Relationship, "EDITED")
# commissioned = graph_db.get_or_create_index(neo4j.Relationship, "ESTABLISHED")
# commissioned = graph_db.get_or_create_index(neo4j.Relationship, "FOUNDED")
# commissioned = graph_db.get_or_create_index(neo4j.Relationship, "FUNDS")
# commissioned = graph_db.get_or_create_index(neo4j.Relationship, "HOSTED")
# commissioned = graph_db.get_or_create_index(neo4j.Relationship, "IS_ENVOY")
# commissioned = graph_db.get_or_create_index(neo4j.Relationship, "LAUNCHED")
# commissioned = graph_db.get_or_create_index(neo4j.Relationship, "LEADS")
# commissioned = graph_db.get_or_create_index(neo4j.Relationship, "MAINTAINS")
# commissioned = graph_db.get_or_create_index(neo4j.Relationship, "MANAGES")
# commissioned = graph_db.get_or_create_index(neo4j.Relationship, "MEMBER_OF")
# commissioned = graph_db.get_or_create_index(neo4j.Relationship, "MONITORS")
# commissioned = graph_db.get_or_create_index(neo4j.Relationship, "OPERATES")
# commissioned = graph_db.get_or_create_index(neo4j.Relationship, "ORGANIZED")
# commissioned = graph_db.get_or_create_index(neo4j.Relationship, "OVERSEES")
# commissioned = graph_db.get_or_create_index(neo4j.Relationship, "PARTNER_WITH")
# commissioned = graph_db.get_or_create_index(neo4j.Relationship, "PRESENTED")
# commissioned = graph_db.get_or_create_index(neo4j.Relationship, "PROVIDES")
# commissioned = graph_db.get_or_create_index(neo4j.Relationship, "RESEARCH_ARM_OF")
# commissioned = graph_db.get_or_create_index(neo4j.Relationship, "SPONSORED")
# commissioned = graph_db.get_or_create_index(neo4j.Relationship, "SUPPORTS")


class MainHandler(BaseHandler):
    def get(self):
        if 'GOOGLEANALYTICSID' in os.environ:
            google_analytics_id = os.environ['GOOGLEANALYTICSID']
        else:
            google_analytics_id = False
        #query_string = "START r=rel(*) RETURN r"
        query_string = "MATCH (n)-[r:ADDRESSES]->(m) WHERE n.type=\"Actor\" AND m.name=\"Broadband Promotion\" RETURN DISTINCT r, n"
        query = neo4j.CypherQuery(graph_db, query_string)
        results = query.execute().data
        nodes = {}
        links = []
        for r in results[0]:
            nodes[r.values[0].start_node['node_id']] = {
                "name":r.values[0].start_node['name'].encode('utf-8'), 
                "group":r.values[0].start_node['type'].encode('utf-8'), 
                "description":r.values[0].start_node['description'].encode('utf-8'), 
                "node":r.values[0].start_node['node_id']}
            description = r.values[0].end_node['description'].encode('utf-8') if 'description' in r.values[0].end_node else ' '
            nodes[r.values[0].end_node['node_id']] = {
                "name":r.values[0].end_node['name'].encode('utf-8'), 
                "group":r.values[0].end_node['type'].encode('utf-8'), 
                "description":description, 
                "node":r.values[0].end_node['node_id']}
            #nodes2 = [dict(t) for t in set([tuple(d.items()) for d in nodes2])]
            #nodes2 = list(set(nodes))
            links.append({"source":r.values[0].start_node['node_id'], "target":r.values[0].end_node['node_id']})
        nodes = nodes.values()
        self.render(
            "index.html",
            page_title='Internet Governance Map',
            page_heading='Map of Internet Governance',
            nodes=nodes,
            links =links,
            google_analytics_id=google_analytics_id,
        )
    def post(self):
        query = self.get_argument("query", None)
        query = self.application.query_builder.build(query)
        tx = session.create_transaction()
        tx.append(query)
        results = tx.execute()
        nodes = {}
        links = []
        for r in results[0]:
            nodes[r.values[0].start_node['node_id']] = {
                "name":r.values[0].start_node['name'].encode('utf-8'), 
                "group":r.values[0].start_node['type'].encode('utf-8'), 
                "description":r.values[0].start_node['description'].encode('utf-8'), 
                "node":r.values[0].start_node['node_id']}
            description = r.values[0].end_node['description'].encode('utf-8') if 'description' in r.values[0].end_node else ' '
            nodes[r.values[0].end_node['node_id']] = {
                "name":r.values[0].end_node['name'].encode('utf-8'), 
                "group":r.values[0].end_node['type'].encode('utf-8'), 
                "description":description, 
                "node":r.values[0].end_node['node_id']}
            #nodes2 = [dict(t) for t in set([tuple(d.items()) for d in nodes2])]
            #nodes2 = list(set(nodes))
            links.append({"source":r.values[0].start_node['node_id'], "target":r.values[0].end_node['node_id']})
        nodes = nodes.values()
        self.write({"nodes":nodes, "links":links, "query":query})



class LoadHandler(BaseHandler):
    def get(self):
        graph_db.clear()
        self.application.data.load_new_data("static/files/nodes.csv")
        # row[0] = node_id
        # row[1] = Name
        # row[2] = type
        # row[3] = description
        # row[4] = abbrev
        # row[5] = url
        # row[6] = contact_info
        # row[7] = year_founded
        # row[8] = date_start
        # row[9] = date_end
        # row[10] = sphere
        # row[11] = recurs
        # row[12] = region
        # row[13] = country
        # row[14] = state
        # row[15] = city
        # missing = []
        # with open("static/files/nodes.csv", mode='r') as infile:
        #     reader = csv.reader(infile)
        #     missing = []
        #     for row in reader:
        #         if row[0] != 'name':
        #             if row[1] == 'Actor':
        #                 new_node = Actor(row[0], row[3], row[2], index)
        #             elif row[1] == 'Initiatives & Events':
        #                 new_node = Event(row[0], row[3], row[2], index)
        #             elif row[1] == 'Laws & Policies':
        #                 new_node = Law(row[0], row[3], row[2], index)
        #             elif row[1] == 'Research & Advocacy':
        #                 new_node = Research(row[0], row[3], row[2], index)
        #             elif row[1] == 'Standards':
        #                 new_node = Standard(row[0], row[3], row[2], index)
        #             elif row[1] == 'Tools & Resources':
        #                 new_node = Tool(row[0], row[3], row[2], index)
        #             if new_node:
        #                 store.save_unique(row[1], "node_id", index, new_node)
        #             else:
        #                 missing.append(row[0])
        #             index +=1
        #     logging.info(missing)
        # def create_relationship(self, node1, node_1_type, node2, node_2_type):
        #     assert {node_1_type, node_2_type}.issubset(TYPES)


class LoadHandler2(BaseHandler):
    def get(self):
        index = 0
        types= []
        #GET NODES
        try:
            nodes = ()
            with open("static/files/nodes.csv", mode='r') as infile:
                reader = csv.reader(infile)
                for row in reader:
                    if row[0] != 'name':
                        nodes = nodes + ({'name':row[0], 'abbrev':row[3], 'type':row[1], "description":row[2], "node_id":index },)
                        types.append(row[1])
                        index = index + 1
            types = list(set(types))
        except Exception, e:
            print "Could not convert to dictionary: " + str(e)
        #GET LIST OF ISSUES
        try: 
            issues = ()
            with open("static/files/issues.csv", mode='r') as infile:
                reader = csv.reader(infile)
                for row in reader:
                    if row[0] != 'name':
                        issues = issues + ({'name':row[0], "type":row[1], "description":row[2], "node_id":index},)
                        index = index + 1
        except Exception, e:
            print "Could not get issues: " + str(e)
        #GET RELATIONSHIPS
        try:
            relationships = ()
            with open("static/files/relationships.csv", mode='r') as infile:
                reader = csv.reader(infile)
                for row in reader:
                    if row[0]!='name1':
                        relationships = relationships + ({'node1':row[0], 'relationship':row[1], 'node2':row[2]}, )
        except Exception, e:
            print "Could not get relationships: " + str(e)
        #clear DB
        graph_db.clear()

        #MAKE A LIST OF INDECES
        indeces = {}
        indeces['Issue'] = graph_db.get_or_create_index(neo4j.Node, 'Issue')
        for type_ in types:
            indeces[type_] = graph_db.get_or_create_index(neo4j.Node, type_)

        batch = neo4j.WriteBatch(graph_db)

        #CREATE ISSUE NODES
        for i in issues:
            n = batch.create(node(node_id=i['node_id'], name=i['name'], description=i['description'], type="Issue"))
            batch.add_labels(n, 'Issue')
            batch.add_indexed_node(indeces['Issue'], 'node_id', index, n)

        #CREATE NODES
        for nod in nodes:
            n = batch.create(node(node_id=nod['node_id'], name=nod['name'].replace('"', ""), abbrev=nod['abbrev'], description=nod['description'], type=nod['type']))
            batch.add_labels(n, nod['type'])
            batch.add_indexed_node(indeces[nod['type']],'node_id', nod['node_id'], n)

        nodes = batch.submit()

        #NEED TO CREATE QUERY TO ADD LINKS TO ISSUES
        for r in relationships:
            query = "START n=node(*), m=node(*) "
            query += "WHERE n.name=\"{0}\" AND m.name=\"{1}\" ".format(r['node1'].replace('"', ""), r['node2'].replace('"', ""))
            query += "CREATE (n)-[:{0}]->(m)" .format(r['relationship'])
            neo4j.CypherQuery(graph_db, query).execute()