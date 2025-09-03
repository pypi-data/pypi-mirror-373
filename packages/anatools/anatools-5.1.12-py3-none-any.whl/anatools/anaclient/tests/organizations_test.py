import pytest


### Fixtures ###
@pytest.fixture(scope="session")
def add_organization_member_fixture(client):
    email = "test@rendered.ai"
    client.add_organization_member(organizationId=client.organization, email=email, role="member")
    return email


### Tests ###
def test_set_organization(client):
    organizationId = client.organization
    workspaceId = client.workspace
    status = client.set_organization(organizationId=organizationId)
    assert status == True
    assert client.organization == organizationId
    status = client.set_workspace(workspaceId=workspaceId)
    assert status == True
    assert client.workspace == workspaceId

def test_get_organizations(client):
    organizations = client.get_organizations()
    assert isinstance(organizations, list)
    assert len(organizations) > 0

def test_edit_organization(client):
    organization = client.get_organizations(organizationId=client.organization)[0]
    status = client.edit_organization(organizationId=organization['organizationId'], name="anatools-edit-organization")
    assert status == True
    organizations = client.get_organizations(organizationId=client.organization)
    assert isinstance(organizations, list)
    assert len(organizations) == 1
    assert organizations[0]['name'] == "anatools-edit-organization"
    status = client.edit_organization(organizationId=organization['organizationId'], name=organization['name'])
    assert status == True
    
def test_get_organization_members(client):
    members = client.get_organization_members(organizationId=client.organization)
    assert isinstance(members, list)
    assert len(members) > 0

def test_get_organization_invites(client, add_organization_member_fixture):
    invites = client.get_organization_invites(organizationId=client.organization)
    assert isinstance(invites, list)
    userinvites = [invite for invite in invites if invite['email'] == add_organization_member_fixture]
    assert len(userinvites) == 1

@pytest.mark.dependency(depends=["test_get_organization_invites"])
def test_remove_organization_invitation(client, add_organization_member_fixture):
    email = add_organization_member_fixture
    status = client.remove_organization_invitation(organizationId=client.organization, email=email)
    assert status == True

# def test_remove_organization_member(client, add_organization_member_fixture):
#     email = add_organization_member_fixture
#     status = client.remove_organization_member(organizationId=client.organization, email=email)
#     assert status == True

# def test_edit_organization_member(client, add_organization_member_fixture):
#     email = add_organization_member_fixture
#     status = client.edit_organization_member(organizationId=client.organization, email=email, role="member")
#     assert status == True
#     members = client.get_organization_members(organizationId=client.organization)
#     usermembers = [member for member in members if member['email'] == email]
#     assert len(usermembers) == 1
#     assert usermembers[0]['role'] == 'member'    
