"""
Introspection API calls.
"""

def getTypes(self):
    """
    Get the data types from the GraphQL schema.
    
    Returns:
        A dictionary of data types from the GraphQL schema
    """
    if self.types: return list(self.types.keys())
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "IntrospectionQuery",
            "query": """query IntrospectionQuery {
                __schema {
                    types {
                        name
                        description
                        kind
                    }
                }
            }"""
        })
    responsedata = response.json()
    returndata = {}
    if 'data' in responsedata and '__schema' in responsedata['data'] and 'types' in responsedata['data']['__schema']:
        for type in responsedata['data']['__schema']['types']:
            if not type['name'].startswith('__') and type['kind'] == 'OBJECT': returndata[type['name']] = type['description']
    self.types = returndata
    return list(returndata.keys())


def getTypeFields(self, typeName):
    """
    Get all fields available for a specific GraphQL type.
    
    Args:
        typeName (str): The name of the GraphQL type to introspect
        
    Returns:
        List of field names available on the specified type
    """
    if typeName in self.fields: return self.fields[typeName]
    query = f"""query {{
        __type(name: \"{typeName}\") {{
            name
            kind
            fields {{
                name
                description
                type {{
                    name
                    kind
                    ofType {{
                        name
                        kind
                    }}
                }}
            }}
        }}
    }}"""
    
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "query": query
        })
    responsedata = response.json()
    returndata = []
    if 'data' in responsedata and '__type' in responsedata['data'] and 'fields' in responsedata['data']['__type']:
        for field in responsedata['data']['__type']['fields']:
            if field['type']['kind'] == 'OBJECT':
                fields = self.getTypeFields(field['type']['name'])
                datastr = f"{field['name']} {{"
                for a in fields: datastr += f"\n  {a}"
                datastr += "\n}"
                returndata.append(datastr)
            elif 'ofType' in field['type'] and field['type']['ofType'] != None and 'kind' in field['type']['ofType'] and field['type']['ofType']['kind'] == 'OBJECT': 
                fields = self.getTypeFields(field['type']['ofType']['name'])
                datastr = f"{field['name']} {{"
                for a in fields: datastr += f"\n  {a}"
                datastr += "\n}"
                returndata.append(datastr)
            else: 
                returndata.append(field['name'])
    self.fields[typeName] = returndata
    return returndata