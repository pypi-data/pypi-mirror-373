class PopulationException(BaseException):
    def __init__(self,  details):
        super().__init__()
        self.details = details