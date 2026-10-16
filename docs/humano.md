# Human-in-the-loop

## Ponto de parada

O grafo pausa antes da única ação de escrita: criar uma reserva na API mock. O portão é exigido sempre que a mensagem contém pedido explícito de agendamento. A recomendação ou a frase do cliente não dispara diretamente o POST.

O interrupt apresenta ação, identificador da opção, serviço, profissional, data/hora, preço, opções consultadas e prazo de validade. A pessoa chamada é o cliente final autenticado, que decide sobre a própria reserva; operação humana pode apoiar exceções fora do corpus, mas não aprova pelo cliente nesta POC.

Respostas aceitas:

- `aprovar`: confirma a opção apresentada;
- `rejeitar`: encerra sem escrita;
- `editar` + `opcao_id`: escolhe outra opção da mesma lista consultada. Uma opção que não foi consultada é rejeitada.

## Prazo e retomada

A aprovação vence em 15 minutos. Uma aprovação recebida depois do prazo é convertida em rejeição e não chega ao nó `registrar_agendamento`. Se ninguém responder, o checkpoint permanece pausado; ao tentar retomar após o prazo, o grafo segue pelo término `aprovacao_expirada`.

O checkpointer é `SqliteSaver`, com banco local `dados/checkpoints.sqlite`. Para retomar, a chamada precisa usar o mesmo `thread_id` (`conversa_id`) e `Command(resume=...)`. O estado pendente sobrevive ao encerramento e reabertura do processo. O banco é local, sem criptografia de aplicação, e não deve conter dados reais nesta POC.

`python -m src.verificar_checkpoint` prova a retomada entre dois processos: o primeiro CLI interrompe, termina, e o segundo CLI abre o mesmo banco e aprova a mesma conversa.

## Idempotência

A escrita deriva SHA-256 de `cliente_id`, `opcaoId` e `dataHoraInicio`. O servidor mock guarda a chave; uma repetição devolve o mesmo identificador e `ja_existia: true`, sem inserir outra reserva. O caso `logs/06-aprovacao-editada.json` contém primeira e segunda respostas e registra `agendamentos_unicos: 1`.

Esta proteção cobre a API mock em memória durante a demonstração. Reiniciar o processo mock limpa suas reservas e chaves; o backend real precisa persistir a chave em armazenamento transacional.
