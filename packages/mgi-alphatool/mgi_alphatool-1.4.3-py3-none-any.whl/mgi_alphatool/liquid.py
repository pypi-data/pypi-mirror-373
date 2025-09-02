class Liquid:
    def __init__(self, id: str, name: str, desc: str, context: 'Context'):
        self.__id = id
        self.__name = name       
        self.__desc = desc
        self.__context = context
    
    def id(self):
        """Get the liquid ID.

        Returns:
            str: The liquid's unique identifier.
        """
        return self.__id