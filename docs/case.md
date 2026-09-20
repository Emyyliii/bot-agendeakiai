# Case — AgendeAkiAI

## Problema e contexto

**Problema em uma frase:** o cliente que procura um serviço de beleza para uma ocasião precisa combinar manualmente ocasião, estilo, orçamento, localização e disponibilidade antes de conseguir escolher um horário.

O usuário que sofre diretamente é o **cliente final que precisa se preparar para um evento** e ainda não sabe qual serviço, profissional ou horário atende melhor à sua necessidade. O agente é acionado pelo cliente, no chat da área do cliente do AgendeAki, durante a descoberta de um serviço e antes da tela convencional de confirmação.

Hoje o cliente navega por filtros de serviço, salão, profissional, preço e horário; compara resultados e reinicia a busca quando uma combinação não existe. A entrada é uma mensagem em linguagem natural e a saída é uma recomendação de até três opções, seguida de confirmação explícita antes de qualquer agendamento. Depois da confirmação, a plataforma registra o agendamento e o cliente recebe a identificação dele.

As regras desta primeira versão são: orçamento máximo e bairro restringem a busca; o pedido atual prevalece sobre o histórico; só se confirma uma opção retornada na consulta da sessão; e cancelamento exige 48 horas de antecedência, enquanto remarcação não tem custo. Não há, por enquanto, regra definida para atraso, falta ou lembrete de confirmação — esses casos são encaminhados para a operação humana.

Os casos difíceis são: preferência atual que contradiz o histórico, cliente inexistente, não haver uma opção compatível e o cliente querer somente comparar, sem autorizar escrita.

## Usuários e interação

| Perfil | O que quer | O que sabe | O que pode fazer |
|---|---|---|---|
| Cliente final — usuário principal | Escolher e agendar um serviço adequado | Sabe a necessidade e as preferências; não conhece catálogo ou disponibilidade | Descrever, corrigir preferências, escolher e confirmar o próprio agendamento |
| Estabelecimento/profissional | Manter serviços e horários corretos | Conhece sua agenda e capacidade | Atualizar catálogo e disponibilidade; não confirma em nome do cliente |
| Operação AgendeAki | Resolver exceções e proteger a experiência | Conhece regras e dados operacionais | Analisar exceções, corrigir dados e tratar cancelamento, atraso ou falta |

O canal é um chat dentro da plataforma Web: ele permite que a pessoa descreva uma ocasião sem conhecer os filtros disponíveis. O cliente inicia a conversa. A primeira mensagem descreve o que procura; em geral são de duas a quatro trocas, até que o agente tenha serviço, bairro e orçamento suficientes ou reconheça que precisa de ajuda humana. A resposta é texto curto com opções estruturadas (serviço, profissional, salão, horário e preço) e, se houver escolha explícita, uma confirmação de agendamento.

Quando uma regra ainda não existe, há conflito que o agente não consegue esclarecer, ou nenhuma opção atende aos filtros mesmo após uma flexibilização oferecida ao cliente, o fluxo termina sem escrita e chama a Operação AgendeAki.

### Diálogo de referência

> Cliente: Quero um penteado clássico para casamento no Centro, até R$ 150.
>
> Agente: Encontrei penteado clássico com Bianca no Studio Aurora, às 15h, por R$ 120. Quer confirmar esta opção?
>
> Cliente: Sim, confirmo.
>
> Agente: Agendamento confirmado. Se quiser cancelar, a regra atual exige antecedência de 48 horas.

O cliente normalmente não informa todos os filtros na primeira mensagem. O agente pergunta apenas pelo filtro que impede a busca; se o histórico disser “moderno” e o cliente pedir “clássico”, usa o pedido atual e informa essa priorização. Só considera que sabe o suficiente quando serviço e os filtros disponíveis permitem consultar opções. A confirmação é uma decisão do cliente, nunca uma inferência do modelo.

## Workflow

1. **ENTRADA** — recebe a mensagem e o identificador do cliente. **[decide: CÓDIGO]**
2. **ENTENDIMENTO** — interpreta ocasião, serviço, estilo, bairro e orçamento; pede o dado mínimo que falta. **[decide: MODELO]**
3. **HISTÓRICO** — consulta preferências e reservas anteriores. Se não existir, registra o erro e continua sem personalização. **[decide: CÓDIGO]**
4. **BUSCA** — consulta catálogo e agenda usando filtros disponíveis. **[decide: CÓDIGO]**
5. **RECOMENDAÇÃO** — compara as opções retornadas e explica a melhor alternativa; o pedido atual tem prioridade sobre o histórico. **[decide: MODELO]**
6. **CONFIRMAÇÃO** — apresenta a opção e espera autorização explícita do cliente. **[decide: CÓDIGO]**
7. **AGENDAMENTO** — grava a reserva somente após confirmação. **[ESCRITA — irreversível nesta POC; confirma: cliente final] [decide: CÓDIGO]**
8. **RETORNO/ESCALONAMENTO** — mostra o resultado ou orienta a Operação quando não for possível resolver. **[decide: CÓDIGO]**

## Sistema e autonomia

O sistema interpreta uma necessidade expressa em linguagem natural, consulta o histórico e o catálogo por HTTP, recomenda opções reais retornadas pela API mock e só grava uma reserva com confirmação explícita. Ele não inventa horários, preços ou regras.

O nível é **agente limitado**: um roteador ou formulário resolve consultas fixas, mas não decide em tempo de execução quais filtros faltam, como interpretar uma ocasião e como explicar uma flexibilização quando não há correspondência exata. A autonomia é limitada porque consultas, autorização e escrita continuam sob controle do código e do cliente.

| Ferramenta | O que faz | Leitura ou escrita? | Reversível? | Contra o que conversa |
|---|---|---|---|---|
| `consultar_historico` | Retorna preferências e agendamentos do cliente | Leitura | Sim | API HTTP mock do AgendeAki |
| `buscar_opcoes` | Retorna opções por serviço, bairro e orçamento | Leitura | Sim | API HTTP mock do AgendeAki |
| `confirmar_agendamento` | Registra a opção confirmada pelo cliente | Escrita | Não nesta POC | API HTTP mock do AgendeAki |

## Justificativa de negócio

O agente é justificado pela interpretação de pedidos incompletos e variados e pela decisão contextual de qual pergunta fazer ou qual alternativa apresentar; um filtro tradicional continua responsável por aplicar as restrições e gravar a reserva. Não é necessário dar ao modelo poder para escrever nem para decidir regras de negócio.

O ganho que será medido é **ações manuais para chegar a uma opção**. A linha de base ainda precisa ser coletada no frontend real do `monorepo-agendeaki`: dez pessoas (ou dez execuções guiadas) realizarão os mesmos cenários, registrando número de telas, filtros preenchidos e tempo. Não há medições reais no repositório ainda; portanto, não declaramos porcentagem de ganho como fato.

O alvo da POC, a validar nessa coleta, é reduzir a mediana de ações de busca por cenário, sem reduzir a taxa de conclusão. A conta que será usada é: `(mediana de ações no fluxo tradicional − mediana de ações com agente) / mediana de ações no fluxo tradicional × 100`, multiplicada pela quantidade mensal de buscas concluídas. É uma hipótese, não um resultado já comprovado.

Para o negócio, a possível redução é de esforço por busca e abandono; para o cliente, é não precisar repetir filtros e receber uma alternativa explicada. Há uma tensão: automatizar demais pode recomendar algo inadequado; por isso o cliente escolhe e confirma, e o caso ambíguo é escalado.

O modo mock custa US$ 0. Para o Mistral Small, a estimativa de tokens e custo está em [modelos.md](modelos.md). O custo de construção é o tempo da equipe. A perda mais importante é uma recomendação inadequada ou reserva indevida; a POC mitiga a segunda com confirmação explícita, mas não promete eliminar a primeira.

## Verificador e sucesso

O verificador construído é `src/verificar.py`. Ele lê os quatro cenários rotulados em `dados/casos-avaliacao.json` e confere, nos logs: escrita apenas no caso confirmado, erro `CLIENTE_NAO_ENCONTRADO` no cliente inexistente e trechos de resposta esperados. A execução é `python -m src.verificar` depois de `python -m src.demo`.

**Critério de sucesso desta POC:** os **4 de 4** cenários rotulados passam no verificador; em particular, **0 de 3** cenários sem confirmação pode registrar agendamento e o cenário de cliente inexistente deve terminar sem queda do programa.

## Dados e privacidade

Os dados são simulados e vivem em `dados/catalogo.json`. Para preservar dificuldade, incluem: divergência entre histórico “moderno” e pedido atual “clássico”; `cliente-inexistente`, que produz registro inexistente; e uma consulta explícita sem reserva, que não pode disparar a ação principal. Os quatro cenários estão nomeados em `dados/casos-avaliacao.json`.

O domínio normalmente toca dados pessoais (nome, histórico e preferências). Nesta POC todos são fictícios. Dados reais não devem entrar no repositório nem no contexto do modelo; em produção, o identificador do cliente e o mínimo necessário devem ser buscados sob autenticação pela integração da plataforma.

## Espaço para as próximas partes

- **RAG (Parte 2):** regras de cancelamento, serviços, políticas de cada salão e descrições de estilos, inicialmente em documentos Markdown/JSON.
- **MCP (Parte 2):** a API HTTP mock de histórico, busca e agendamento será a candidata a servidor MCP quando a integração com o `monorepo-agendeaki` for feita.
- **LangChain (Parte 2):** pode orquestrar recuperação de regras e ferramentas quando houver mais de uma fonte de conhecimento; não é necessário nesta POC.
- **Multiagente (Parte 3):** um agente de recomendação e outro de operação poderiam ser separados apenas se as regras e a revisão humana crescerem; ainda não há justificativa para isso.

## Maior risco

O maior risco é o catálogo/agenda real não expor dados consistentes o bastante para uma recomendação confiável, especialmente quando há mudança de disponibilidade entre busca e confirmação. O plano B é tratar a API do `monorepo-agendeaki` como fonte de verdade, revalidar a opção no momento da escrita e encaminhar a falha de disponibilidade ao cliente sem confirmar a reserva.
