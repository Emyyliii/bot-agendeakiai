# Protocolo de medição da linha de base

Esta coleta ainda não foi realizada. Este arquivo existe para que a equipe registre medições reais, sem substituir observação por estimativa.

## Procedimento

1. Abrir o frontend do `monorepo-agendeaki` em uma sessão limpa.
2. Entregar um dos dez cenários abaixo à pessoa que fará o teste.
3. Cronometrar do primeiro filtro até a seleção de uma opção; registrar também telas visitadas e filtros preenchidos.
4. Repetir o mesmo cenário no chat do AgendeAkiAI, sem confirmar a reserva.
5. Preencher a tabela com o valor observado e calcular a mediana de cada fluxo.

| Caso | Cenário | Tempo tradicional (s) | Telas/filtros tradicionais | Tempo agente (s) | Trocas com agente | Concluiu? |
|---|---|---:|---:|---:|---:|---|
| 01 | Penteado clássico, casamento, Centro, até R$ 150 | — | — | — | — | — |
| 02 | Maquiagem natural, formatura, até R$ 150 | — | — | — | — | — |
| 03 | Corte profissional, entrevista, Moema, até R$ 100 | — | — | — | — | — |
| 04 | Comparar opções sem reservar | — | — | — | — | — |
| 05 | Preferência atual contradiz histórico | — | — | — | — | — |
| 06 | Serviço sem opção no orçamento | — | — | — | — | — |
| 07 | Bairro sem opção para o serviço | — | — | — | — | — |
| 08 | Pedido incompleto, precisa informar orçamento | — | — | — | — | — |
| 09 | Cliente sem histórico | — | — | — | — | — |
| 10 | Pedido fora do escopo de beleza | — | — | — | — | — |

## Cálculo

Para tempo: `(mediana tradicional − mediana agente) / mediana tradicional × 100`.

Para esforço: usar a mesma fórmula com telas/filtros tradicionais e trocas do agente. O resultado só deve entrar no `case.md` depois de as dez linhas estarem preenchidas com observações reais.
