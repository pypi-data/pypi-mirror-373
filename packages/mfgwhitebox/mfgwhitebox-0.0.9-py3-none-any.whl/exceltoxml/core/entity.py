class Entity:
    def __init__(self, entity_type, uri, title, class_name, component):
        self.type = entity_type
        self.uri = uri
        self.title = title
        self.class_name = class_name
        self.component = component
        self.fields = []
        self.titles = []
        self.types = []
        self.records = []
        self.foreign_keys = []
