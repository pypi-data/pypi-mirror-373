class Resource():
    def __init__(self, id):
        self.id = id
    
class Dataset(Resource):
    '''This class encapsulates datasets in the ENVRI-HUB.
    it is made up of two attributes:
    + Data: the actual data, either a datastructure or a data access object
    + Metadata: information about the data, expressed as a dictionary-like structure
    '''
    def __init__(self, id):
        self.id = id

class Service(Resource):
    pass