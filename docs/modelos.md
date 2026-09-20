# Modelo — AgendeAkiAI

## Decisão

Esta primeira versão usa exclusivamente o **Mistral Small**, pelo identificador disponível na conta `mistral-small-2603`. A decisão privilegia uma prova de conceito barata, com chamadas curtas e compatibilidade direta com o código Python exigido pela disciplina.

O projeto usa a biblioteca `openai` apenas como cliente compatível de Chat Completions; ela aponta para `LLM_BASE_URL=https://api.mistral.ai/v1`. Isso não envia chamadas para outro provedor. A chave configurada em `OPENAI_API_KEY` é a chave da Mistral, mantida fora do Git no `.env`.

## Por que esse modelo atende ao caso

| Eixo | Necessidade do AgendeAkiAI | Decisão |
|---|---|---|
| Interpretação de linguagem natural | Entender pedidos incompletos sobre ocasião, serviço, bairro e orçamento | O Mistral Small é suficiente para esta POC curta |
| Tool calling e saída estruturada | O modelo precisa decidir entre consultar histórico, buscar opções ou responder | Usar Chat Completions compatível com ferramentas tipadas |
| Latência | O cliente espera a resposta no chat | Manter uma chamada curta por passo, com máximo de 600 tokens de saída |
| Contexto | A POC usa mensagem atual, histórico curto e poucas opções | Não há documento longo nem necessidade de contexto ampliado |
| Dados | Histórico e catálogo são dados pessoais simulados | Enviar apenas o mínimo necessário; nenhum dado real entra no repositório |
| Custo | O grupo optou por não contratar outros modelos | Desenvolver e demonstrar em modo mock, que custa US$ 0; usar Mistral somente quando necessário |

## Conta de custo

O agente tem teto de seis passos e no máximo 4.000 tokens totais. A estimativa da chamada real deve usar os tokens registrados no log:

```text
(tokens de entrada × preço de entrada da Mistral)
+ (tokens de saída × preço de saída da Mistral)
= custo por execução
```

Para 100 execuções, multiplica-se o custo por execução por 100; para o semestre, pelo volume estimado de execuções. Os valores de preço não são fixados neste documento porque mudam; devem ser consultados na tabela oficial da Mistral antes de qualquer uso pago. A demonstração com `python -m src.demo` usa `mock-agendeakiai-v1` e tem custo US$ 0.

## Verificação do modelo

Os cinco casos de domínio a verificar com o mesmo prompt são:

1. Casamento, orçamento baixo, visual elegante e clima quente.
2. Entrevista, corte profissional, rápido e econômico.
3. Formatura, maquiagem natural em clima quente.
4. Cliente que muda de preferência no meio da conversa.
5. Pedido fora do escopo ou sem informação suficiente.

Nesta entrega, a demonstração reproduz quatro cenários determinísticos no modo mock e verifica segurança de ferramentas, não qualidade probabilística do modelo remoto. A avaliação real do Mistral será registrada quando a equipe decidir consumir a franquia disponível; ela deve guardar prompt, resposta, tokens, latência e resultado de cada caso.

## Quando mudar de ideia

A escolha será revista se o Mistral Small falhar repetidamente em chamar a ferramenta correta, não respeitar a confirmação antes da escrita, exceder o orçamento de custo/latência ou não interpretar adequadamente os cinco casos acima. Até lá, a menor opção que resolve a POC é manter apenas Mistral Small.
