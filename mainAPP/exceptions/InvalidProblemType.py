class InvalidProblemType(Exception):
    '''
        Exception to be thrown if user
        doesn't provide comma seperated
        value of problems for creating
        a challenge.
    '''
    def __init__(self,message="Invalid Specified problem types should be seperated by comma's."):
        super().__init__(self,message)
