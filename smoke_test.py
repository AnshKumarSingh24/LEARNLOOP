from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
signup = client.post('/auth/signup', json={'email':'alice@example.com','password':'strong-password'})
assert signup.status_code == 200, signup.text
token = signup.json()['access_token']
headers = {'Authorization': f'Bearer {token}'}

for filename, source in [
    ('networks.txt', b'Networks connect computers. TCP provides reliable delivery and congestion control.'),
    ('security.txt', b'Network security protects communication. Encryption and authentication reduce risk.'),
]:
    response = client.post('/documents/upload', files={'file': (filename, source, 'text/plain')}, headers=headers)
    assert response.status_code == 200, response.text
    assert response.json()['vector_indexed'] is True

library = client.get('/library/search', params={'q':'reliable network communication security','k':5}, headers=headers)
assert library.status_code == 200, library.text
assert library.json()['results']

document_id = client.get('/documents/'+response.json()['document']['id'], headers=headers).json()['id']
artifact = client.post(f'/documents/{document_id}/artifacts/mindmap', json={'instruction':'Connect the concepts'}, headers=headers)
assert artifact.status_code == 200, artifact.text
course = client.post(f'/documents/{document_id}/create-course', json={'goal':'exam','daily_minutes':15,'level':1}, headers=headers)
assert course.status_code == 200, course.text
course_id = course.json()['course']['id']
next_response = client.get(f'/courses/{course_id}/next', headers=headers)
assert next_response.status_code == 200, next_response.text
concept_id = next_response.json()['concept_id']
progress = client.post('/progress', json={'concept_id':concept_id,'correct':True,'quality':4}, headers=headers)
assert progress.status_code == 200, progress.text
assert progress.json()['repetitions'] == 1
saved = client.get(f'/courses/{course_id}/progress', headers=headers)
assert saved.status_code == 200 and saved.json()['overall_mastery'] > 0
pdf = client.get(f'/courses/{course_id}/export/pdf', headers=headers)
assert pdf.status_code == 200 and pdf.headers['content-type'].startswith('application/pdf')
scorm = client.get(f'/courses/{course_id}/export/scorm', headers=headers)
assert scorm.status_code == 200 and scorm.content.startswith(b'PK')
print('authenticated library smoke test passed:', course_id)
