from py2neo import neo4j
from py2neo import node, rel, cypher
from py2neo.packages.urimagic import URI
import sys
from models import *
import csv
import re
from handlers.handlers import graph_db

issue_list = [{
            "issue":"DNS Security",
            "synonyms":["dns","dns security", "dnssec"]
        }, 
        {
            "issue":"IPv6 Adoption", 
            "synonyms":["ipv6","ipv6 adoption", "ip"]
        }, {
            "issue":"Broadband Promotion", 
            "synonyms":["broadband","broadband promotion"]
        }, {
            "issue":"Child Pornography", 
            "synonyms":["cp","child pornography", "child porn"]
        }, {
            "issue":"Internet Gambling",
            "synonyms":["internet gambling","gambling"]
        }]
relationships = ["address", "addresses" "deals", "deal", "attends", "attend" "focuses", "focus" "undertakes", "research", "tackles", "tackle", "concerning" "sees", "about", "on"]
type_list = [{
            "synonyms": ["initiatives", "events", "conferences", "parties", "proposal", "plans", "schemes", "strategies"],
            "type":"Initiatives & Events"
        },
        {
            "synonyms": ["laws", "policies", "rules", "bylaws", "bills", "decrees", "resolutions", "orders", "procedures"],
            "type":"Laws & Policies"
        },
        {
            "synonyms": ["organizations", "groups", "firm", "corporation", "association", "society", "institutions", "people", "leaders", "individuals", "humans"],
            "type":"Actor"
        }, 
        {
            "synonyms": ["research", "investigations", "studies", "study", "findings", "experiments", "analysis", "support", "backing"],
            "type":"Research & Advocacy"
        },
        {
            "synonyms": ["standards", "protocols", "norms", "guidelines", "criteria", "norms"],
            "type":"Standards"
        },
        {
            "synonyms": ["tools", "information", "applications", "apps", "instruments", "materials"],
            "type":"Tools & Resources"
        }
        ]
TYPES = ["Actor", "Person", "Initiatives and Events", "Issue", "Laws and Policies", "Research and Advocacy", "Standards", "Tools and Resources"]
field_names = ["node_id", "name", "type", "description", "abbrev", "url", "contact_info", "year_founded", "date_start", "date_end", "sphere", "recurs", "region", "country", "state", "city"]



class QueryBuilder(object):
    def build(self, query):
        q = query.split()
        rel = [s for s in relationships if s in q]
        rel_word = q.index(rel[0])
        cat = ''
        issue = ''
        for typ in type_list:
            for word in q[0:q.index(rel[0])]:
                if any(word.lower() in s for s in typ['synonyms']):
                    cat = typ['type']
        for iss in issue_list:
            for word in q[rel_word+1:]:
                if any(word.lower() in s for s in iss['synonyms']):
                    issue = iss['issue']
        logging.info(rel)
        logging.info(issue)
        logging.info(cat)
        return "MATCH (n)-[r:ADDRESSES]->(m) WHERE n.type=\""+ cat +"\" AND m.name=\""+ issue +"\" RETURN DISTINCT r, n"

class DataLoader(object):
    def create_node(self, label, node_):
        new_node = []
        for key, value in node_.iteritems():
            if value:
                new_node.append(key + ':"' + value.replace('"', '\"').replace("\n", " ") + '"')
        new_node = ', '.join(new_node)
        new_node = new_node
        query_string = "CREATE (n:{0} {{ {1} }})".format(label.replace(" & ",""), new_node)
        try:
            query = neo4j.CypherQuery(graph_db, query_string)
            query.execute()
        except Exception, e:
            print "Could not create node: " + str(e)

    def get_node_by_name(self, name):
        query_string = 'START n=node(*) MATCH n WHERE n.name="{0}" RETURN n'.format(name)
        results = neo4j.CypherQuery(graph_db, query_string).execute()
        return results[0][0]

    def get_node_by_index_and_name(index_name, node_name):
        index = graph_db.get_index(neo4j.Node, index_name)
        results = index.get("name",node_name)[0]
        return results

    #reads a file and makes a list of all the different types of objects and turns them into indexes.
    def generate_node_indeces_from_file(self, filename):
        with open(filename, mode="r") as infile:
            reader = csv.reader(infile)
            types = []
            for row in reader:
                if row[1] != "name":
                    types.append(row[2])
                else:
                    field_names = row
            types = list(set(types))
            for type_ in types:
                graph_db.get_or_create_index(neo4j.Node, type_)
            return field_names

    def load_nodes_from_file(self, filename):
        field_names = generate_node_indeces_from_file("static/files/nodes.csv")
        batch = neo4j.WriteBatch(graph_db)
        num_nodes = 0
        with open(filename, mode="r") as infile:
            reader = csv.reader(infile)
            for row in reader:
                new = {}
                if row[1] !="name":
                    for i in range(0, len(row)):
                        new[field_names[i]] = row[i]
                    new_node = batch.create(node(new))
                    index = graph_db.get_index(neo4j.Node, new['type'])
                    batch.add_indexed_node(index, "name", new['name'], new_node)
                    batch.add_labels(new_node, new['type'])
                    num_nodes +=1
        batch.submit()

    def generate_relationships_indeces_from_file(self, filename):
        batch = neo4j.WriteBatch(graph_db)
        with open(filename, mode="r") as infile:
            reader = csv.reader(infile)
            relationship_types = []
            for row in reader:
                relationship_types.append(row[1])
            relationship_types = list(set(relationship_types))
        for r in relationship_types:
            graph_db.get_or_create_index(neo4j.Relationship, r)
        return relationship_types












