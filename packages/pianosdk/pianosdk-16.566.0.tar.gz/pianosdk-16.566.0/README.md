Piano API SDK
======
This is simple wrapper for Piano API.

Requirements
------
Python 3.7+

Examples
------

VX API
```python
from pianosdk import Client, AccessTokenStorage

host = 'sandbox' # use 'production', 'sandbox' or custom endpoint here, like 'https://api-ap.piano.io'
client = Client(api_host=host, api_token='TOKEN', private_key='PRIVATE_KEY')
response = client.access_api.list('AID')
print(response)
response = client.publisher_term_api.list('AID')
print(response)
response = client.userref_create('UID', 'EMAIL')
print(f'User ref for [uid=UID, email=EMAIL]: {response}')
response = client.parse_webhook_data('WEBHOOK_DATA')
print(f'Webhook event: [{type(response)}] {response}')
token_storage = AccessTokenStorage(client.config)
response = token_storage.get_access_token('UNKNOWN_RID')
print(f'Access token for unknown rid: {response}')
token_storage.parse_access_tokens('TAC_VALUE')
# or use
token_storage.parse_access_tokens_from_cookies_string('ALL_COOKIES_STRING')
response = token_storage.get_access_token('RID')
print(f'Access token for known rid: {response}')
```

ID API
```python
from pianosdk import Client
from pianosdk.id import PublisherLoginRequest
client = Client(environment='sandbox', api_token='TOKEN')
request = PublisherLoginRequest(aid='AID', email='test@example.com', password='1234')
response = client.publisher_identity_api.login(authorization=client.config.api_token, body=request)
print(response)
```
