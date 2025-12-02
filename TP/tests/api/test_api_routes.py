def test_invalid_uuid(client):
    # Test sans mock, juste validation format ID
    response = client.get('/triangulation/ceci-nest-pas-un-uuid')
    # Selon ton plan, on attend 400
    assert response.status_code == 400

def test_method_not_allowed(client):
    response = client.post('/triangulation/1234')
    assert response.status_code == 405