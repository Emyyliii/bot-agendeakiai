# Modelo — AgendeAkiAI

## Decisão

O modo padrão é mock determinístico e custa US$ 0. Mistral Small (`mistral-small-2603`) é uma opção para redigir a resposta final, acionada por `MODO=mistral`; não escolhe ferramentas, filtros, regras ou autorização. O código já verificou as fontes e suficiência antes da redação. Essa escolha mantém o custo fora do caminho padrão e dá um local claro para avaliar a qualidade de linguagem natural.

O projeto usa `openai` como cliente compatível com Chat Completions, apontado por padrão para `https://api.mistral.ai/v1`. A chave é lida de `OPENAI_API_KEY` no `.env`, ignorado pelo Git. A avaliação Mistral não foi rodada e nenhum resultado de qualidade é declarado.

## Adequação e limites

| Eixo | Decisão atual |
|---|---|
| Interpretação de filtros | Código PT-BR simples identifica serviço, bairro e orçamento. Não foi delegado ao modelo |
| Recuperação de fatos | API mock estruturada para opções e busca lexical em Markdown para regras |
| Saída remota | Zero-shot; JSON com `resultado`, `fontes`, `suficiente`, validado por Pydantic |
| Segurança | O modelo recebe a resposta já verificada; código conserva as fontes e suficiência originais |
| Latência e tokens | Uma chamada final com timeout de 10 s e no máximo 400 tokens de saída; uso fica registrado no evento de modelo |
| Custo | Zero no mock; modo remoto recusa a chamada se o teto conservador por bytes exceder 4.000 tokens estimados ou US$ 0,01. As taxas por milhão devem vir da tabela oficial vigente; o custo real fica registrado pelo uso reportado pela API |

O modo remoto não deve ser tratado como garantia de correção: a validação Pydantic confere formato e tipos, não a verdade semântica do texto. Respostas de regras devem ser comparadas com o corpus e os logs.

## Testes propostos

Usar as dez perguntas em `dados/perguntas-rag.json` e os casos de conversa da demonstração. Para cada resposta Mistral, guardar prompt e hash, texto, fontes, suficiência, tokens, latência e acerto contra o gabarito. A comparação da frase em `docs/prompts.md` está pendente; o modo mock mede somente fluxo e segurança do código.

## Quando rever a decisão

Reavaliar se as respostas Mistral mudarem fatos/fontes, falharem o contrato, trouxerem texto confuso ou excederem custo e latência aceitáveis. O modo mock continua adequado para testar gates e integração local independentemente da qualidade probabilística.
