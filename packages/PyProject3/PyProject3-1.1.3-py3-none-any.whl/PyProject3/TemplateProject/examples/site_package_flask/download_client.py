import requests

API_HOST = 'http://localhost:5000'


def download():
    api_url = f'{API_HOST}/ttsa/download/a.pcm'
    content = requests.get(api_url)
    with open('a.pcm', 'wb') as f:
        f.write(content.content)


def helloworld():
    api_url = f'{API_HOST}/ttsa/offline'
    res = requests.get(api_url, json=dict(text=''))
    print(res.json())


helloworld()
