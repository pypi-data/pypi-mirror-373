"""
Agent Functions
"""

def get_data_types(self):
    """Retrieve a list of data types available on the Platform.
    
    Returns
    -------
    list[str]
        The data types available on the Platform.
    """
    return self.ana_api.getTypes()


def get_data_fields(self, type):
    """Retrieve information about the fields that can be returned for a specific data type.
    
    Parameters
    ----------
    type : str
        The data type to retrieve fields for.
    
    Returns
    -------
    list[str]
        Information about the fields available for the specified data type.
    """
    if type not in self.get_data_types(): raise ValueError(f"Invalid data type: {type}")
    return self.ana_api.getTypeFields(type)
