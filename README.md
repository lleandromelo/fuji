# Assistente virtual para a Fuji Locações

Este repositório contém um assistente virtual em Python pensado para responder
clientes pelo WhatsApp com base nas informações do catálogo público da Fuji
Locações (https://locacoesfuji.estoquenow.site/). O bot foi estruturado para
atender às demandas mais comuns:

- confirmar se um determinado modelo (por exemplo, uma cadeira) está
  disponível;
- informar a quantidade de itens em estoque;
- enviar um resumo do acervo com links/fotos representativas;
- responder saudações e dúvidas frequentes, guiando o cliente durante a
  conversa.

A automação utiliza uma abordagem 100% determinística (regras simples e
tratamento básico da linguagem natural), evitando dependências externas ou
modelos proprietários.

## Estrutura do projeto

```
.
├── app.py                      # Webhook Flask compatível com Twilio WhatsApp
├── data/
│   └── inventory.json          # Catálogo em formato JSON utilizado pelo bot
├── requirements.txt            # Dependências necessárias no ambiente de produção
├── whatsapp_assistant/
│   ├── config.py               # Carregamento de configurações via variáveis de ambiente
│   ├── intent_detection.py     # Regras para identificar o tipo da pergunta
│   ├── inventory.py            # Leitura e busca dentro do inventário
│   ├── message_handler.py      # Montagem das respostas (texto + mídias)
│   └── text_utils.py           # Funções utilitárias para normalizar texto
└── tests/
    └── test_message_handler.py # Testes unitários da camada de negócio
```

## Pré-requisitos

- Python 3.11 ou superior.
- Conta no [Twilio](https://www.twilio.com/) habilitada para WhatsApp
  (modo sandbox ou número homologado).

## Como executar localmente

1. Crie um ambiente virtual e instale as dependências:

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. Copie o arquivo `.env.example` para `.env` e ajuste os valores conforme o seu
   ambiente:

   ```bash
   cp .env.example .env
   ```

   - `INVENTORY_PATH`: caminho para o catálogo em JSON.
   - `MEDIA_LIMIT`: quantidade máxima de fotos enviadas por resposta.
   - Credenciais do Twilio (`TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN` e o número
     WhatsApp habilitado).

3. Garanta que o arquivo `data/inventory.json` reflita o seu acervo. O projeto
   inclui um exemplo ilustrativo — substitua pelos dados reais exportados do
   site.

4. Inicie o servidor Flask:

   ```bash
   flask --app app run --port 8000
   ```

5. Configure o webhook no painel do Twilio (ou use `ngrok` em ambiente local)
   apontando para `https://SEU_DOMINIO/webhook`. Toda mensagem recebida será
   encaminhada para o `MessageHandler`, que retornará a resposta formatada
   com texto e, quando aplicável, URLs de imagens.

## Atualizando o inventário

- Faça o download/exportação do catálogo no portal
  https://locacoesfuji.estoquenow.site/ (o site permite visualizar a quantidade
  em estoque de cada item). Transcreva ou exporte esses dados para o arquivo
  `data/inventory.json` utilizando o formato exemplificado.
- Cada item pode ter diversos `aliases` — nomes alternativos pelos quais os
  clientes costumam perguntar (ex.: “cadeira tiffany”, “cadeira tiffany branca”).
  Esses apelidos facilitam a correspondência das mensagens com o item correto.
- A propriedade `image_url` deve apontar para uma URL pública (HTTPS). O Twilio
  fará o download direto para incluir a mídia na resposta.

## Executando os testes automatizados

Os testes validam a camada de regras, garantindo que perguntas comuns resultem
nas respostas esperadas. Para rodá-los:

```bash
python -m unittest
```

## Próximos passos sugeridos

- Automatizar a coleta do inventário (por exemplo, via script que consome a API
  do EstoqueNow quando disponível).
- Persistir conversas e carrinhos de reserva em um banco de dados externo.
- Conectar o assistente a um CRM para abertura automática de ordens de serviço
  após a confirmação do pedido pelo cliente.
