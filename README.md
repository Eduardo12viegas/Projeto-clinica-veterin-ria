# Clínica Veterinária – Estrutura de Dados

Sistema em Python que simula o ciclo de um atendimento veterinário: chegada do animal, espera por
consultório, diagnóstico, medicamentos e procedimentos, alta, fechamento do prontuário e pagamento.

## Como executar

```
python main.py
```

Sem bibliotecas externas. Os dados ficam só na memória: a cada execução o programa carrega
tutores, animais e estoque de exemplo (inclui um lote de vacina vencido para mostrar as perdas).

Para simular um atendimento completo pelo menu:
1. **Atendimento > Solicitar atendimento** (normal e emergência) e **Ver fila**.
2. **Atendimento > Chamar próximo animal** (abre o prontuário).
3. **Prontuários > Gerenciar um prontuário**: marcar itens como Alterado na árvore.
4. Incluir medicamentos e procedimentos.
5. Dar alta, **fechar e pagar**. O sistema indica o próximo animal da fila.

## Organização dos arquivos

| Arquivo | Responsabilidade |
|---|---|
| `estruturas.py` | `No`, `Lista`, `Fila`, `NoArvore`, `Arvore` (genéricas, feitas à mão) |
| `atendimento.py` | `Solicitacao`, `Consultorio`, `ControleAtendimento` (filas e consultórios) |
| `diagnostico.py` | `Componente`, árvore pré-definida do animal, marcar e exibir |
| `estoque.py` | `Lote`, `Produto`, `Perda`, `Estoque` |
| `prontuario.py` | `Prontuario`, `ItemMedicamento`, `Procedimento` |
| `pagamento.py` | `Pagamento`, `Consumo` |
| `clinica.py` | classe `Clinica`: junta tudo e concentra as regras (tutores, animais, fechamento) |
| `cli.py`, `main.py` | menus de terminal (só perguntam e mostram; as regras ficam na `Clinica`) |

Estruturas genéricas ficam de um lado (`estruturas.py`) e as regras da clínica do outro. Nenhuma
estrutura nativa do Python (list, dict, deque...) guarda os dados do problema.

## Combinações de estruturas

### 1. Fila + Fila: atendimento com prioridade para emergência
- **Onde:** `ControleAtendimento` (`atendimento.py`), com `fila_emergencia` e `fila_normal`.
- **Métodos:** `chegada`, `proximo_da_fila`, `chamar_proximo`, `liberar_consultorio`,
  `fila_em_ordem`. Na `Clinica`: `solicitar_atendimento` e `chamar_proximo`.
- **Como funciona:** o próximo vem da fila de emergência; se ela estiver vazia, vem da normal.
  Cada fila mantém a ordem de chegada do seu grupo.
- **Por que é adequada:** enfileirar e desenfileirar são O(1) e a prioridade vira uma checagem
  simples de "a fila de emergência está vazia?".
- **Desvantagem de uma fila só:** para uma emergência passar na frente seria preciso inserir no
  meio da fila (percorrer até o ponto certo, O(n)) ou reordenar tudo.

### 2. Lista + Fila: estoque com vários lotes por produto
- **Onde:** `Estoque.produtos` (Lista de `Produto`), cada `Produto.lotes` é uma Fila de `Lote`.
- **Métodos:** `registrar_compra`, `baixar`, `_consumir`, `descartar_vencidos`,
  `ajustar_quantidade`, `alertas`; e `Fila.filtrar`, `Fila.ultimo`.
- **Como funciona:** a baixa percorre a lista até o produto (O(n)) e consome a fila a partir do
  primeiro lote, que é o mais antigo (O(1) por lote). Lote esgotado sai da fila. Lotes vencidos
  saem com `Fila.filtrar` (O(l)) e viram registros de `Perda`.
- **Por que é adequada:** os lotes entram por ordem de compra, então a fila já garante "primeiro
  o mais antigo" sem precisar ordenar.
- **Desvantagem de uma lista única de lotes:** misturaria produtos diferentes e seria preciso
  ordenar por data de compra (ou varrer tudo) a cada baixa.

### 3. Lista + Lista: tutores e seus animais
- **Onde:** `Clinica.tutores` (Lista de `Tutor`), cada `Tutor.animais` é uma Lista de `Animal`.
- **Métodos:** `cadastrar_tutor`, `buscar_tutor`, `cadastrar_animal`, `buscar_animal`,
  `remover_tutor`, `remover_animal`.
- **Como funciona:** `buscar_animal` percorre a lista de tutores até o CPF e depois a lista de
  animais daquele tutor: O(t + a). Um tutor pode ter quantos animais quiser.
- **Por que é adequada:** o animal pertence a um tutor e o nome do animal só é único dentro do
  mesmo tutor, por isso a busca usa o CPF junto com o nome.
- **Desvantagem de uma lista única de animais:** repetiria os dados do tutor em cada animal e
  não deixaria claro a quem cada animal pertence (nomes como "Rex" se repetem entre tutores).

## Outras estruturas
- **Árvore de sistemas do animal** (`Arvore`, `NoArvore`): árvore geral (não binária e não de
  busca): cada nó tem uma Lista de filhos (0 a N). A exibição indentada usa percurso em
  profundidade em pré-ordem (O(n)). Cada prontuário recebe a sua própria cópia da árvore.
- **Lista** também guarda os prontuários abertos, medicamentos e procedimentos de cada
  prontuário, pagamentos, consumos, perdas e os consultórios.

## Regras principais
- O animal só entra na fila se o tutor e o animal existirem e ele ainda não estiver na espera
  ou em atendimento. Tutor ou animal em atendimento não podem ser removidos.
- Medicamentos e procedimentos podem ser adicionados e removidos até o fechamento.
- O prontuário só fecha depois da alta do animal.
- No fechamento: baixa do estoque pelo lote mais antigo, registro do consumo (tutor, animal e
  medicamento), registro do pagamento (PIX, cartão à vista ou parcelado, dinheiro) e liberação
  do consultório, com a indicação do próximo animal da fila.
- Lotes vencidos são descartados e registrados como perda; existe alerta de estoque mínimo e
  ajuste de inventário.