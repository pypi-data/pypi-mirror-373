import httpx

class RequestServicoApi:
    def __init__(self, url, token):
        self.url = url
        self.token = token

    async def handler(self, *, mensagem_atualizacao: dict):
        async with httpx.AsyncClient() as client:
            response = await client.post(self.url, headers={"Authorization": f"Bearer {self.token}"}, json=mensagem_atualizacao)

            if response.status_code != 200:
                raise Exception(f"Erro ao fazer request ao servico de API: {response.status_code}")
            
            return response.json()