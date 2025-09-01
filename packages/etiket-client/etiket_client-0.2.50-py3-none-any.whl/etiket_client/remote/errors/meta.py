
class EtiketExceptionsMeta(type):
    def __getitem__(cls, x):
        return getattr(cls, x)
    
    def __contains__(cls, x):
        return hasattr(cls, x)