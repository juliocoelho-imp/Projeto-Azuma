# 🎬 Roteiro de Apresentação — Sistema Azuma HelpDesk
**Duração estimada: ~5 minutos**

---

## ⏱ PARTE 1 — Introdução (0:00 – 0:40)

**[Câmera no rosto ou tela inicial do sistema]**

> "Olá! Hoje vou apresentar o Azuma, um sistema de HelpDesk desenvolvido com Python, Flask e PostgreSQL. O objetivo é centralizar a gestão de chamados de suporte técnico, permitindo que operadores atendam, acompanhem e resolvam tickets de forma organizada e eficiente."

> "Vou mostrar as funcionalidades que já estão implementadas, as novas funcionalidades que propomos, e os diagramas de classes e de casos de uso do sistema."

---

## ⏱ PARTE 2 — Funcionalidades Existentes (0:40 – 2:30)

### Dashboard (0:40 – 1:10)
**[Mostrar tela do Dashboard]**

> "Começando pelo Dashboard — a visão central do sistema. Aqui temos KPIs em tempo real: chamados abertos, em andamento, concluídos e prazos vencidos."

> "Também é possível ver a distribuição por prioridade — Alta, Média e Baixa —, a carga de chamados por operador, e as categorias mais frequentes. Tudo atualizado dinamicamente."

### Central de Chamados — Listagem e Filtros (1:10 – 1:40)
**[Mostrar tela de Tickets]**

> "Na Central de Chamados vemos todos os tickets. Podemos filtrar por status: Aberto, Em Andamento, Pausado ou Concluído. Também dá pra buscar por título, empresa ou operador, e ordenar por prioridade, tempo gasto ou prazo mais próximo."

> "Cada linha da tabela exibe o ID, título, empresa, prioridade com badge colorido, operador, prazo com alerta visual e o timer de tempo de atendimento."

### Abertura e Edição de Chamados (1:40 – 2:00)
**[Mostrar modal de novo ticket e de edição]**

> "Para abrir um novo chamado basta clicar em 'Novo Ticket'. Preenchemos título, descrição, categoria, prioridade, mesa, operador, empresa e o prazo SLA. Também é possível editar qualquer campo após a abertura."

### Timer e Finalização (2:00 – 2:30)
**[Mostrar toggle do timer e modal de finalização]**

> "O sistema tem um timer integrado por chamado. Ao iniciar o atendimento, o cronômetro roda em tempo real. É possível pausar e retomar. Ao finalizar, o operador registra a solução e o chamado é encerrado com o tempo total computado."

> "Chamados encerrados podem ser reabertos a qualquer momento, registrando automaticamente essa ação no histórico de comentários."

---

## ⏱ PARTE 3 — Novas Funcionalidades Propostas (2:30 – 3:30)

**[Mostrar os diagramas ou slide de lista]**

> "Com base na análise do sistema, propomos cinco novas funcionalidades para a próxima versão:"

**1. Cadastro de Empresas**
> "Ao invés de digitar o nome da empresa livremente em cada chamado, o sistema passará a ter um cadastro centralizado de empresas clientes, com CNPJ e e-mail de contato."

**2. Avaliação de Atendimento**
> "Após o encerramento, o cliente poderá avaliar o atendimento com uma nota de 1 a 5 estrelas e um comentário opcional — permitindo medir a satisfação e identificar pontos de melhoria."

**3. Configuração de SLA**
> "Administradores poderão criar regras de SLA: definindo prazos em horas para cada nível de prioridade. O sistema calculará automaticamente a data limite ao abrir um chamado."

**4. Notificações Internas**
> "O sistema enviará notificações automáticas: quando um chamado for atribuído, quando o prazo estiver próximo de vencer, e quando um chamado for reaberto."

**5. Controle de Acesso por Perfil**
> "A model de Usuário ganhará um campo de perfil: Cliente, Operador e Administrador — cada um com permissões distintas no sistema."

---

## ⏱ PARTE 4 — Diagrama de Classes (3:30 – 4:10)

**[Mostrar o Diagrama de Classes]**

> "No Diagrama de Classes temos três entidades originais do sistema: Usuario, Chamado e Comentario."

> "Usuario tem relação 1 para N com Chamado e com Comentario — um usuário pode abrir vários chamados e escrever vários comentários."

> "Chamado é a entidade central: possui título, descrição, status, prioridade, categoria, operador, timer e prazo SLA."

> "Comentario registra cada interação no chamado, podendo ser público ou privado."

> "As entidades novas propostas são: Empresa, SLA, Avaliacao e Notificacao — todas ligadas a Chamado ou Usuario por chaves estrangeiras, ampliando o modelo sem quebrar o que já existe."

---

## ⏱ PARTE 5 — Diagrama de Casos de Uso (4:10 – 4:45)

**[Mostrar o Diagrama de Casos de Uso]**

> "No Diagrama de Casos de Uso temos três atores: Cliente, Operador e Administrador."

> "O Cliente pode abrir chamados, acompanhar o status, avaliar o atendimento e receber notificações — sendo as duas últimas funcionalidades novas."

> "O Operador tem acesso à listagem, atribuição, atualização de status, controle do timer, comentários, finalização, busca e filtros — e também ao novo recurso de anexar arquivos."

> "O Administrador acessa o Dashboard, gerencia usuários e empresas, configura SLAs e pode gerar relatórios — todas essas funções administrativas são propostas como melhorias."

---

## ⏱ PARTE 6 — Conclusão (4:45 – 5:00)

**[Câmera no rosto ou tela inicial]**

> "O Azuma já oferece uma base sólida para gestão de chamados: dashboard em tempo real, controle de tempo, filtros avançados e histórico de atendimentos. Com as novas funcionalidades propostas — SLA automatizado, avaliações, notificações e controle de acesso — o sistema evolui para uma solução completa de HelpDesk corporativo."

> "Obrigado!"

---

## 📋 Dicas para a gravação

- **Fale pausado** — 5 minutos é curto, não apresse.
- **Mostre cada tela** enquanto fala sobre ela.
- **Destaque os diagramas** em tela cheia ao mencionar cada entidade/ator.
- Grave em ambiente silencioso com boa iluminação frontal.
- Se usar slides, use fundo escuro (#0f172a) e texto branco para combinar com o tema do sistema.
