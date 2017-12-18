# Serialization of information for JSON endpoints


def serialize(self):
    print 'this is the self:', self
    return{
        'name': self['name'],
        'description': self['description'],
        'id': self['id'],
        'price': self['price'],
        'course': self['course']
    }


def serialize_resto(self):
    return{
        'name': self['name'],
        'id': self['id']
    }


def serialize_item(self):
    return{
        'name': self['name'],
        'description': self['description'],
        'id': self['id'],
        'price': self['price'],
        'course': self['course']
    }
