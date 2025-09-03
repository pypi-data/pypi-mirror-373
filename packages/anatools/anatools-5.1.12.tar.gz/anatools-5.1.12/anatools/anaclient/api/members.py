"""
Members API calls.
"""

def getMembers(self, organizationId=None, limit=100, cursor=None):
    fields = "\n".join(self.getTypeFields("Member"))
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "getMembers",
            "variables": {
                "organizationId": organizationId,
                "limit": limit,
                "cursor": cursor
            },
            "query": f"""query 
                getMembers($organizationId: String, $limit: Int, $cursor: String) {{
                    getMembers(organizationId: $organizationId, limit: $limit, cursor: $cursor) {{
                        {fields}
                    }}
                }}"""})
    return self.errorhandler(response, "getMembers")


def getInvitations(self, organizationId=None, limit=100, cursor=None):
    fields = "\n".join(self.getTypeFields("Invitation"))
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "getInvitations",
            "variables": {
                "organizationId": organizationId,
                "limit": limit,
                "cursor": cursor
            },
            "query": f"""query 
                getInvitations($organizationId: String, $limit: Int, $cursor: String) {{
                    getInvitations(organizationId: $organizationId, limit: $limit, cursor: $cursor) {{
                        {fields}
                    }}
                }}"""})
    return self.errorhandler(response, "getInvitations")


def addMember(self, organizationId, email, role):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "addMember",
            "variables": {
                "organizationId": organizationId,
                "email": email,
                "role": role
            },
            "query": """mutation 
                addMember($organizationId: String!, $email: String!, $role: String) {
                    addMember(organizationId: $organizationId, email: $email, role: $role)
                }"""})
    return self.errorhandler(response, "addMember")


def removeMember(self, organizationId, email):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "removeMember",
            "variables": {
                "organizationId": organizationId,
                "email": email,
            },
            "query": """mutation 
                removeMember($organizationId: String!, $email: String!) {
                    removeMember(organizationId: $organizationId, email: $email)
                }"""})
    return self.errorhandler(response, "removeMember")


def editMember(self, organizationId, email, role):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "editMember",
            "variables": {
                "organizationId": organizationId,
                "email": email,
                "role": role
            },
            "query": """mutation 
                editMember($organizationId: String!, $email: String!, $role: String!) {
                    editMember(organizationId: $organizationId, email: $email, role: $role)
                }"""})
    return self.errorhandler(response, "editMember")
