"""
Organizations API calls.
"""

def getOrganizations(self, organizationId=None, limit=100, cursor=None, fields=None):
    if fields is None: fields = self.getTypeFields("Organization")
    fields = "\n".join(fields)
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "getOrganizations",
            "variables": {
                "organizationId": organizationId,
                "limit": limit,
                "cursor": cursor
            },
            "query": f"""query 
                getOrganizations($organizationId: String, $cursor: String, $limit: Int,) {{
                    getOrganizations(organizationId: $organizationId, cursor: $cursor, limit: $limit) {{
                        {fields}
                    }}
                }}"""})
    return self.errorhandler(response, "getOrganizations")


def editOrganization(self, organizationId, name):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "editOrganization",
            "variables": {
                "organizationId": organizationId,
                "name": name
            },
            "query": """mutation 
                editOrganization($organizationId: String!, $name: String!) {
                    editOrganization(organizationId: $organizationId, name: $name) 
                }"""})
    return self.errorhandler(response, "editOrganization")
