
"""Base class for models."""


class BaseModel(object):
    """Base for database models."""

    '''
    #def __init__(self, app):
    def __init__(self):
        """Get collection instance from db."""
        # self.collection = app.database[self.__class__.__name__.lower()]
        self.name = self.__class__.__name__.lower()
        print()
        print([self.__class__.__name__.lower()])
        print()
        #self.collection = app['mongo'][[self.__class__.__name__.lower()]]
    

    def __getattribute__(self, name):
        """Override get attribute."""
        try:
            return object.__getattribute__(self, name)
        except AttributeError:
            return object.__getattribute__(self.collection, name)
    '''
    @staticmethod
    def serialize(data):
        """Seriaze basic response of document."""
        for item in data:
            item['_id'] = str(item['_id'])
        return data
