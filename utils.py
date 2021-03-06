from py2neo import neo4j
from py2neo import node, rel, cypher
from py2neo.packages.urimagic import URI
import sys
from models import *
import csv
import re
from handlers.handlers import graph_db
from logging import info

issue_list = [{
            "issue":"DNS Security",
            "synonyms":["dns", "dns security", "dnssec"]
        }, 
        {
            "issue":"IPv6 Adoption", 
            "synonyms":["ipv6","ipv6 adoption", "ip", "ip v6"]
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
relationships = [
                "address", "addresses", "deals", "deal", "attends", 
                "attend" "focuses", "focus" "undertakes", "research", 
                "tackles", "tackle", "concerning" "sees", "about", "on", "study",
                "exist"]
type_list = [{
            "synonyms": [
                "initiatives", "events", "conferences", "parties", "proposal", 
                "plans", "schemes", "strategies"],
            "type":"Initiatives & Events"
        },
        {
            "synonyms": [
                "laws", "policies", "rules", "bylaws", "bills", "decrees", 
                "resolutions", "orders", "procedures"],
            "type":"Laws & Policies"
        },
        {
            "synonyms": [
                "who", "organizations", "groups", "firm", "corporation", 
                "association", "society", "institutions", "people", 
                "leaders", "individuals", "humans"],
            "type":"Actor"
        }, 
        {
            "synonyms": [
                "research", "investigations", "studies", "study", 
                "findings", "experiments", "analysis", "support", "backing"],
            "type":"Research & Advocacy"
        },
        {
            "synonyms": [
                "standards", "protocols", "norms", "guidelines", 
                "criteria", "norms"],
            "type":"Standards"
        },
        {
            "synonyms": [
                "tools", "information", "applications", "apps", 
                "instruments", "materials"],
            "type":"Tools & Resources"
        }
        ]
TYPES = [
    "Actor", "Person", "Initiatives and Events", "Issue", "Laws and Policies", 
    "Research and Advocacy", "Standards", "Tools and Resources"]
field_names = [
    "node_id", "name", "type", "description", "abbrev", "url", "contact_info", 
    "year_founded", "date_start", "date_end", "sphere", "recurs", "region", 
    "country", "state", "city"]



class QueryBuilder(object):
    def build(self, query):
        q = query.split()
        q = [re.sub('[^A-Za-z0-9]+', '', word) for word in q]
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
        info(rel) #Relationship not used for now. 
        info(issue)
        info(cat)
        query = 'MATCH (n)-[r:ADDRESSES]->(m) WHERE n.type="{}" '.format(cat)
        query += 'AND m.name="{}" '.format(issue)
        query += '''RETURN r, n.node_id, n.name, n.type, 
                            n.description, m.node_id, m.name, m.type, 
                            m.description'''
        return query

class DataLoader(object):
    @classmethod
    def generate_node_indeces(self, filename):
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
        batch = neo4j.WriteBatch(graph_db)
        num_nodes = 0
        field_names = self.generate_node_indeces(filename)
        with open(filename, mode="r") as infile:
            reader = csv.reader(infile)
            for row in reader:
                new = {}
                if row[1] !="name":
                    for i in range(0, len(row)):
                        new[field_names[i]] = row[i].decode('utf-8').strip()
                    new_node = batch.create(node(new))
                    index = graph_db.get_index(neo4j.Node, new['type'])
                    batch.add_indexed_node(index, "name", 
                        new['name'].strip(), new_node)
                    batch.add_labels(new_node, new['type'])
                    num_nodes +=1
        info("Loaded: " + str(num_nodes) + " nodes.")
        batch.submit()

    @classmethod
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

    #because searching for nodes only by name is very slow, you need to get all the indeces from each node.
    #This will make creating the relationships faster
    def load_relationships_from_file(self, relationship_filename, node_filename):
        relationship_types = self.generate_relationships_indeces_from_file(relationship_filename)
        batch = neo4j.WriteBatch(graph_db)
        num_relationships = 0
        error_relationships = []
        #get indeces from nodes
        node_dict = {}
        with open(node_filename, mode="r") as infile:
            reader = csv.reader(infile)
            for row in reader:
                node_dict[row[1]] = row[2]
        #make relationships
        with open(relationship_filename, mode="r") as infile:
            reader = csv.reader(infile)
            for row in reader:
                if row[1] != "relationship":
                    try:
                        node_1 = graph_db.get_indexed_node(node_dict[row[0]], "name", row[0].decode('utf-8').strip())
                        node_2 = graph_db.get_indexed_node(node_dict[row[2]], "name", row[2].decode('utf-8').strip())
                        batch.create(rel(node_1, row[1], node_2))
                        num_relationships +=1
                    except Exception, e:
                        error_relationships.append({"node1":row[0].decode('utf-8').strip(), "rel":row[1], "node2":row[2].decode('utf-8').strip(), "error":str(e)})
        results = batch.submit()
        info("The following relationships could not be created:")
        info(error_relationships)

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

    def get_node_by_index_and_name(self, index_name, node_name):
        index = graph_db.get_index(neo4j.Node, index_name)
        results = index.get("name",node_name)[0]
        return results




















