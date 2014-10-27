class Actor(object):
    def __init__(self, name=None, abbrev=None, description=None, node_id=None):
        self.name = name
        self.abbrev = abbrev
        self.description = description
        self.node_id = node_id
        self.label = "Actor"

    def __str__(self):
        return self.name

class Event(object):
    def __init__(self, name=None, abbrev=None, description=None, node_id=None):
        self.name = name
        self.abbrev = abbrev
        self.description = description
        self.node_id = node_id
        self.label = "Initiatives and Events"

    def __str__(self):
        return self.name

class Issue(object):
    def __init__(self, name=None, description=None, node_id=None):
        self.name = name
        self.description = description
        self.node_id = node_id
        self.label = "Issue"
    
    def __string__(self):
        return self.name

class Law(object):
    def __init__(self, name=None, abbrev=None, description=None, node_id=None):
        self.name = name
        self.abbrev = abbrev
        self.description = description
        self.node_id = node_id
        self.label = "Laws and Policies"

    def __str__(self):
        return self.name

class Person(object):
    def __init__(self, name=None, abbrev=None, description=None, node_id=None):
        self.name = name
        self.abbrev = abbrev
        self.description = description
        self.node_id = node_id
        self.label = "Person"

    def __str__(self):
        return self.name

class Research(object):
    def __init__(self, name=None, abbrev=None, description=None, node_id=None):
        self.name = name
        self.abbrev = abbrev
        self.description = description
        self.node_id = node_id
        self.label = "Research and Advocacy"

    def __str__(self):
        return self.name

class Standard(object):
    def __init__(self, name=None, abbrev=None, description=None, node_id=None):
        self.name = name
        self.abbrev = abbrev
        self.description = description
        self.node_id = node_id
        self.label = "Standards"

    def __str__(self):
        return self.name

class Tool(object):
    def __init__(self, name=None, abbrev=None, description=None, node_id=None):
        self.name = name
        self.abbrev = abbrev
        self.description = description
        self.node_id = node_id
        self.label = "Tools and Resources"

    def __str__(self):
        return self.name
