# EventGen AI

Sistema de Otimização de Equipes para Eventos com Algoritmos Genéticos

Trabalho acadêmico — Disciplina de Inteligência Artificial

---

## Objetivo do Projeto

O EventGen AI demonstra a aplicação prática de Algoritmos Genéticos (AG) para resolver um problema real de otimização combinatória: a distribuição de equipes de segurança, brigadistas e equipes médicas entre as diferentes áreas de um evento.

O sistema permite cadastrar eventos, definir os recursos disponíveis, registrar as áreas do evento com suas características e, a partir desses dados, acionar o Algoritmo Genético para encontrar automaticamente a melhor distribuição possível dos recursos.

---

## Estrutura da Aplicação

```
eventgen/
├── app.py                          # Ponto de entrada da aplicação
├── requirements.txt                # Dependências Python
├── eventgen.db                     # Banco de dados SQLite (gerado automaticamente)
├── README.md
└── app/
    ├── __init__.py                 # Factory da aplicação Flask
    ├── models/
    │   ├── database.py             # Conexão e inicialização do SQLite
    │   ├── event_model.py          # Operações CRUD de eventos
    │   ├── area_model.py           # Operações CRUD de áreas
    │   └── optimization_model.py  # Persistência dos resultados
    ├── services/
    │   ├── genetic_algorithm.py    # Implementação completa do AG
    │   └── optimization_service.py # Orquestração entre AG e modelos
    ├── routes/
    │   ├── event_routes.py         # Rotas de eventos
    │   ├── area_routes.py          # Rotas de áreas
    │   └── optimization_routes.py  # Rota de execução da IA
    ├── templates/
    │   ├── base.html               # Layout base com navbar
    │   ├── index.html              # Listagem de eventos
    │   ├── event_form.html         # Formulário de cadastro
    │   └── event_detail.html       # Detalhes, áreas e resultado
    └── static/
        ├── css/main.css            # Estilos da aplicação
        ├── js/main.js              # Scripts auxiliares
        └── img/logo.png            # Logo do sistema
```

---

## Organização do Código

A aplicação segue uma arquitetura em camadas com separação de responsabilidades:

- **Models** — acesso e persistência de dados via SQLite
- **Services** — lógica de negócio e o Algoritmo Genético
- **Routes** — controladores HTTP (Blueprint Flask)
- **Templates** — interface HTML com Bootstrap 5

---

## Funcionamento do Algoritmo Genético

### Problema

Dado um conjunto de áreas de um evento, cada uma com um público estimado e uma prioridade, e um conjunto fixo de recursos disponíveis (seguranças, brigadistas, equipes médicas), encontrar a distribuição que maximiza a cobertura proporcional e prioritária de todas as áreas.

---

### Cromossomos

Cada cromossomo representa uma solução candidata completa. Ele é composto por três vetores de pesos reais, um para cada tipo de recurso (seguranças, brigadistas, equipes médicas), com um peso por área.

```
Cromossomo:
  security_weights    = [w1, w2, ..., wN]   # pesos para seguranças
  firefighter_weights = [w1, w2, ..., wN]   # pesos para brigadistas
  medical_weights     = [w1, w2, ..., wN]   # pesos para equipes médicas
```

Os pesos são normalizados antes da decodificação para garantir que 100% dos recursos sejam distribuídos. A decodificação converte os pesos em contagens inteiras, distribuindo os recursos restantes (por arredondamento) para as áreas de maior peso.

---

### Fitness

A função fitness avalia a qualidade de cada cromossomo atribuindo uma pontuação que reflete quão bem os recursos foram distribuídos.

**Fatores positivos:**

| Fator | Peso | Descrição |
|---|---|---|
| `coverage_score` | 30 | Cobertura mínima por área (seguranças, brigadistas, médicos por 100 pessoas) |
| `priority_score` | 25 | Distribuição proporcional às prioridades das áreas |
| `balance_score`  | 15 | Equilíbrio entre a proporção de público e de recursos recebidos |

**Fatores negativos (penalidades):**

| Penalidade | Valor | Condição |
|---|---|---|
| `critical_penalty` | -50 × déficit | Área crítica com cobertura abaixo de 100% |
| `coverage_penalty` | -20 × déficit | Qualquer área com cobertura abaixo de 50% |

Mínimos de referência utilizados:
- Seguranças: 1 por 100 pessoas
- Brigadistas: 0,5 por 100 pessoas
- Equipes médicas: 0,3 por 100 pessoas

---

### Seleção

Utiliza **Torneio** com tamanho configurável (padrão: 5 candidatos). Cinco indivíduos aleatórios são sorteados da população e o de maior fitness é selecionado como pai. Esse método equilibra pressão seletiva e diversidade genética.

---

### Crossover

Implementado como **Crossover Uniforme**. Para cada posição (gene) dos vetores de pesos, cada filho recebe o gene de um dos pais com probabilidade 50%. Isso resulta em alta diversidade genética e exploração ampla do espaço de soluções.

Taxa padrão: 85%

---

### Mutação

Implementada como **Perturbação Gaussiana**. Com probabilidade `mutation_rate`, um valor amostrado de uma distribuição normal (média 0, desvio padrão 0,2) é somado ao peso original. Os pesos são limitados ao intervalo [0,01; ∞).

Taxa padrão: 15%

---

### Evolução

| Parâmetro | Valor padrão |
|---|---|
| Tamanho da população | 80 |
| Máximo de gerações | 200 |
| Elitismo | 4 melhores preservados |
| Parada antecipada | 40 gerações sem melhoria |

**Ciclo por geração:**
1. Avaliar fitness de todos os indivíduos
2. Preservar os 4 melhores (elitismo)
3. Selecionar pais por torneio
4. Aplicar crossover uniforme
5. Aplicar mutação gaussiana
6. Substituir população
7. Verificar critério de parada

---

## Fluxo do Sistema

```
Cadastro de Evento
       ↓
Definição de Recursos (seguranças, brigadistas, equipes médicas)
       ↓
Cadastro de Áreas (nome, público estimado, prioridade)
       ↓
Execução do Algoritmo Genético
       ↓
Resultado: melhor fitness, gerações, tempo, distribuição por área
       ↓
Visualização em tabela e cards por área
```

---

## Como Executar

### Pré-requisitos

- Python 3.9 ou superior
- pip

### Instalação

```bash
# 1. Clonar ou extrair o projeto
cd eventgen

# 2. (Opcional, mas recomendado) Criar ambiente virtual
python -m venv venv
source venv/bin/activate        # Linux / macOS
venv\Scripts\activate           # Windows

# 3. Instalar dependências
pip install -r requirements.txt

# 4. Executar a aplicação
python app.py
```

A aplicação estará disponível em: `http://127.0.0.1:5000`

---

## Dependências Necessárias

| Pacote | Versão mínima | Descrição |
|---|---|---|
| Flask | 3.0.0 | Framework web Python |

O banco de dados SQLite é nativo do Python — nenhuma instalação adicional é necessária.

---

## Como Testar

### Exemplo 1 — Festival de Música

**Evento:**
- Nome: Festival de Verão
- Participantes: 8000
- Seguranças: 40 | Brigadistas: 20 | Equipes médicas: 10

**Áreas:**

| Área | Público | Prioridade |
|---|---|---|
| Palco Principal | 4000 | Critica |
| Entrada / Saída | 1500 | Alta |
| Praça de Alimentação | 1500 | Media |
| Área VIP | 500 | Alta |
| Estacionamento | 500 | Baixa |

**Resultado esperado:** O AG deve concentrar proporcionalmente mais recursos no Palco Principal e nas áreas de prioridade Alta/Critica, enquanto garante cobertura mínima nas demais.

---

### Exemplo 2 — Evento Corporativo

**Evento:**
- Nome: Conferência Tech 2025
- Participantes: 1200
- Seguranças: 10 | Brigadistas: 6 | Equipes médicas: 4

**Áreas:**

| Área | Público | Prioridade |
|---|---|---|
| Auditório Central | 600 | Critica |
| Recepção | 300 | Alta |
| Área de Exposição | 200 | Media |
| Estacionamento | 100 | Baixa |

---

## Considerações Acadêmicas

O algoritmo implementado é **real e funcional**. Nenhum resultado é simulado ou fixo. Cada execução pode produzir resultados ligeiramente diferentes (comportamento estocástico do AG), mas converge consistentemente para distribuições de qualidade elevada graças ao elitismo e ao critério de parada por estagnação.

O gráfico de evolução do fitness exibido na interface demonstra visualmente a convergência do algoritmo ao longo das gerações.
