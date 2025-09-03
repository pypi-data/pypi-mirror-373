
def test_get_data_types(client):
    datasets = client.get_data_types()
    print(datasets)
    assert isinstance(datasets, list)
    assert len(datasets) > 0

def test_get_data_fields(client):
    fields = client.get_data_fields(type='Dataset')
    print(fields)
    assert isinstance(fields, list)
    assert len(fields) > 0
    assert 'datasetId' in fields
