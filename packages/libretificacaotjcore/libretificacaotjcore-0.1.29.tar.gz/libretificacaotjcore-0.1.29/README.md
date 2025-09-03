# 🛠️ LIBRETIFICACAOTJCORE

## 📝 Descrição

O Objetivo desse serviço é:
- Centralizar conexão com filas no rabbit e consumo de mensagens
- Centralizar conexão banco de dados no mongodb para os serviços de retificação da TJ
- Centralizar todas as operações de criação, leitura e atualização de arquivos
- Centralizar todas as operações de criação, leitura e atualização de protocolos
- Disponibilizar metodos para tratativas de arquivos
- Disponibilizar Dtos e Enums comuns em todos os serviços de retificações

## ⚙️ Configuração
nessesário ter o [uv astral](https://docs.astral.sh/uv/getting-started/installation/) instalado

Com o UV instalado, execute o comando abaixo para criar o arquivo de configuração:

```bash
    uv sync
```

## 📺 Como publicar?

Para publicar o serviço, execute o comando abaixo:

```bash
    uv build
```
e depois

```bash
    twine upload dist/*
```

Obs: É necessário informa o token do pypi para que o comando funcione
