"""
Algoritmo Genético para Otimização da Distribuição de Equipes em Eventos
==========================================================

Este módulo implementa um Algoritmo Genético (AG) para resolver o problema de
alocação de recursos na gestão de eventos. O objetivo é distribuir pessoal de
segurança, brigadistas e equipes médicas entre as áreas do evento de forma
ótima.

Conceitos-chave:
- Cromossomo: uma lista de alocações, uma por área, cada alocação = [segurança, brigadista, médico]
- População: uma coleção de soluções candidatas (cromossomos)
- Aptidão: uma pontuação que mede quão boa é uma solução
- Seleção: escolher os melhores indivíduos para reprodução
- Crossover: combinar dois pais para gerar descendentes
- Mutação: alterar genes aleatoriamente para manter a diversidade
"""

import random
import copy
import time
from typing import List, Tuple, Dict


# ---------------------------------------------------------------------------
# Classes de Dados
# ---------------------------------------------------------------------------

class AreaConfig:
    """Armazena a configuração de uma única área do evento."""

    PRIORITY_WEIGHTS = {
        'Baixa': 1.0,
        'Media': 1.5,
        'Alta': 2.5,
        'Critica': 4.0
    }

    def __init__(self, area_id: int, name: str, estimated_people: int, priority: str):
        self.area_id = area_id
        self.name = name
        self.estimated_people = estimated_people
        self.priority = priority
        self.priority_weight = self.PRIORITY_WEIGHTS.get(priority, 1.0)


class ResourcePool:
    """Recursos totais disponíveis para o evento."""

    def __init__(self, security: int, firefighters: int, medical: int):
        self.security = max(0, security)
        self.firefighters = max(0, firefighters)
        self.medical = max(0, medical)


# ---------------------------------------------------------------------------
# Representação do Cromossomo
# ---------------------------------------------------------------------------

class Chromosome:
    """
    Um cromossomo representa uma solução completa para o problema de alocação.

    Estrutura: lista de tamanho N (número de áreas), em que cada elemento é uma
    tupla (segurança_alocada, brigadista_alocado, médico_alocado).

    O cromossomo usa codificação proporcional: cada gene armazena um peso em
    ponto flutuante em [0, 1] para cada tipo de recurso por área. As quantidades
    reais são calculadas normalizando os pesos e multiplicando pelos recursos totais.
    """

    def __init__(self, num_areas: int):
        self.num_areas = num_areas
        # Três vetores de pesos: um por tipo de recurso
        # Cada peso está em [0.1, 1.0] para evitar alocação zero
        self.security_weights = [random.uniform(0.1, 1.0) for _ in range(num_areas)]
        self.firefighter_weights = [random.uniform(0.1, 1.0) for _ in range(num_areas)]
        self.medical_weights = [random.uniform(0.1, 1.0) for _ in range(num_areas)]

    def decode(self, resources: ResourcePool) -> List[Tuple[int, int, int]]:
        """
        Converte os pesos em ponto flutuante em alocações inteiras de recursos.
        Garante que todos os recursos sejam distribuídos sem desperdício.
        """
        allocations = []

        for weights, total in [
            (self.security_weights, resources.security),
            (self.firefighter_weights, resources.firefighters),
            (self.medical_weights, resources.medical)
        ]:
            weight_sum = sum(weights) or 1.0
            normalized = [w / weight_sum for w in weights]
            counts = [int(n * total) for n in normalized]

            # Distribuir as unidades restantes para as áreas de maior peso
            remainder = total - sum(counts)
            if remainder > 0:
                indexed = sorted(range(len(weights)), key=lambda i: weights[i], reverse=True)
                for i in range(remainder):
                    counts[indexed[i % len(indexed)]] += 1

            allocations.append(counts)

        # Agrupar em tuplas por área
        return list(zip(allocations[0], allocations[1], allocations[2]))


# ---------------------------------------------------------------------------
# Função de Aptidão
# ---------------------------------------------------------------------------

class FitnessEvaluator:
    """
    Avalia a qualidade de um cromossomo (alocação de recursos).

    Fórmula de Aptidão:
    -------------------
    fitness = coverage_score + priority_score + balance_score - penalty_score

    Fatores positivos:
    - coverage_score: cada área recebe pelo menos os recursos mínimos necessários.
    - priority_score: áreas de alta prioridade recebem proporcionalmente mais recursos.
    - balance_score: os recursos são distribuídos proporcionalmente ao tamanho do público.

    Fatores negativos (penalidades):
    - idle_penalty: recursos alocados além da capacidade da área são desperdiçados.
    - critical_penalty: áreas críticas com cobertura insuficiente recebem penalidade forte.
    - imbalance_penalty: o desvio padrão entre as proporções penaliza distribuições desiguais.
    """

    MIN_SECURITY_PER_100 = 1.0
    MIN_FIREFIGHTER_PER_100 = 0.5
    MIN_MEDICAL_PER_100 = 0.3

    def __init__(self, areas: List[AreaConfig], resources: ResourcePool):
        self.areas = areas
        self.resources = resources
        self.total_people = sum(a.estimated_people for a in areas) or 1

    def evaluate(self, chromosome: Chromosome) -> float:
        allocations = chromosome.decode(self.resources)
        fitness = 0.0
        penalties = 0.0

        # Calcular o total ponderado para a normalização da participação esperada
        weighted_total = sum(a.estimated_people * a.priority_weight for a in self.areas) or 1.0

        for i, area in enumerate(self.areas):
            sec, fire, med = allocations[i]
            people = area.estimated_people or 1
            weight = area.priority_weight

            # ── Requisitos mínimos (linha de base por 100 pessoas) ──────────────
            min_sec  = max(1, (people / 100) * self.MIN_SECURITY_PER_100)
            min_fire = max(1, (people / 100) * self.MIN_FIREFIGHTER_PER_100)
            min_med  = max(1, (people / 100) * self.MIN_MEDICAL_PER_100)

            sec_cov  = min(sec  / min_sec,  2.0)   # cap at 2× minimum
            fire_cov = min(fire / min_fire, 2.0)
            med_cov  = min(med  / min_med,  2.0)
            coverage = (sec_cov + fire_cov + med_cov) / 3.0

            # ── Pontuação de cobertura ───────────────────────────────────────────
            fitness += coverage * weight * 30.0

            # ── Pontuação de participação ponderada pela prioridade ─────────────
            # A participação esperada é proporcional a (pessoas × peso_de_prioridade)
            expected_share = (people * weight) / weighted_total
            actual_share = (
                (sec  / (self.resources.security    or 1)) +
                (fire / (self.resources.firefighters or 1)) +
                (med  / (self.resources.medical      or 1))
            ) / 3.0
            share_diff = abs(actual_share - expected_share)
            priority_score = max(0.0, 1.0 - share_diff / (expected_share + 0.01))
            fitness += priority_score * weight * 25.0

            # ── Pontuação de equilíbrio (recompensa a distribuição proporcional) ─
            people_ratio = people / self.total_people
            ratio = actual_share / (people_ratio + 1e-6)
            # Ideal ratio for a neutral area = 1.0; for Critica = priority_weight
            balance = 1.0 / (1.0 + abs(ratio - weight))
            fitness += balance * 15.0

            # ── Penalidades ────────────────────────────────────────────────────
            if area.priority == 'Critica' and coverage < 1.0:
                penalties += (1.0 - coverage) * 60.0

            if area.priority == 'Alta' and coverage < 0.75:
                penalties += (0.75 - coverage) * 30.0

            if coverage < 0.5:
                penalties += (0.5 - coverage) * 25.0

        fitness -= penalties
        n = len(self.areas) or 1
        fitness = fitness / n
        return max(0.0, fitness)


# ---------------------------------------------------------------------------
# Algoritmo Genético
# ---------------------------------------------------------------------------

class GeneticAlgorithm:
    """
    Orquestrador do algoritmo genético.

    Parâmetros:
    ----------
    population_size : número de soluções mantidas por geração.
    max_generations : parada rígida para o loop de evolução.
    crossover_rate  : probabilidade de dois pais gerarem descendentes por crossover.
    mutation_rate   : probabilidade de qualquer gene individual sofrer mutação.
    elitism_count   : número de melhores indivíduos preservados sem alteração a cada geração.
    tournament_size : número de candidatos comparados na seleção por torneio.
    """

    def __init__(
        self,
        population_size: int = 80,
        max_generations: int = 200,
        crossover_rate: float = 0.85,
        mutation_rate: float = 0.15,
        elitism_count: int = 4,
        tournament_size: int = 5
    ):
        self.population_size = population_size
        self.max_generations = max_generations
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate
        self.elitism_count = elitism_count
        self.tournament_size = tournament_size

    # ------------------------------------------------------------------
    # Inicialização da População
    # ------------------------------------------------------------------

    def _initialize_population(self, num_areas: int) -> List[Chromosome]:
        """Cria uma população inicial de cromossomos aleatórios."""
        return [Chromosome(num_areas) for _ in range(self.population_size)]

    # ------------------------------------------------------------------
    # Seleção: Torneio
    # ------------------------------------------------------------------

    def _tournament_selection(
        self, population: List[Chromosome], fitness_scores: List[float]
    ) -> Chromosome:
        """
        Seleção por torneio: escolhe aleatoriamente `tournament_size` indivíduos
        e retorna o de maior aptidão. Isso equilibra pressão seletiva e diversidade.
        """
        candidates = random.sample(range(len(population)), min(self.tournament_size, len(population)))
        best = max(candidates, key=lambda i: fitness_scores[i])
        return copy.deepcopy(population[best])

    # ------------------------------------------------------------------
    # Crossover: Uniforme
    # ------------------------------------------------------------------

    def _crossover(self, parent1: Chromosome, parent2: Chromosome) -> Tuple[Chromosome, Chromosome]:
        """
        Crossover uniforme: para cada gene (peso da área), cada pai contribui com
        probabilidade de 50%. Isso promove uma exploração diversificada do espaço de soluções.
        """
        if random.random() > self.crossover_rate:
            return copy.deepcopy(parent1), copy.deepcopy(parent2)

        child1 = Chromosome(parent1.num_areas)
        child2 = Chromosome(parent1.num_areas)

        for i in range(parent1.num_areas):
            if random.random() < 0.5:
                child1.security_weights[i] = parent1.security_weights[i]
                child2.security_weights[i] = parent2.security_weights[i]
            else:
                child1.security_weights[i] = parent2.security_weights[i]
                child2.security_weights[i] = parent1.security_weights[i]

            if random.random() < 0.5:
                child1.firefighter_weights[i] = parent1.firefighter_weights[i]
                child2.firefighter_weights[i] = parent2.firefighter_weights[i]
            else:
                child1.firefighter_weights[i] = parent2.firefighter_weights[i]
                child2.firefighter_weights[i] = parent1.firefighter_weights[i]

            if random.random() < 0.5:
                child1.medical_weights[i] = parent1.medical_weights[i]
                child2.medical_weights[i] = parent2.medical_weights[i]
            else:
                child1.medical_weights[i] = parent2.medical_weights[i]
                child2.medical_weights[i] = parent1.medical_weights[i]

        return child1, child2

    # ------------------------------------------------------------------
    # Mutação: Perturbação Gaussiana
    # ------------------------------------------------------------------

    def _mutate(self, chromosome: Chromosome) -> Chromosome:
        """
        Mutação gaussiana: adiciona um pequeno valor aleatório (de uma distribuição
        normal) a cada peso com probabilidade `mutation_rate`.
        Os pesos são limitados a [0.01, 2.0] para manter valores válidos.
        """
        for i in range(chromosome.num_areas):
            if random.random() < self.mutation_rate:
                chromosome.security_weights[i] = max(
                    0.01, chromosome.security_weights[i] + random.gauss(0, 0.2)
                )
            if random.random() < self.mutation_rate:
                chromosome.firefighter_weights[i] = max(
                    0.01, chromosome.firefighter_weights[i] + random.gauss(0, 0.2)
                )
            if random.random() < self.mutation_rate:
                chromosome.medical_weights[i] = max(
                    0.01, chromosome.medical_weights[i] + random.gauss(0, 0.2)
                )
        return chromosome

    # ------------------------------------------------------------------
    # Loop Principal de Evolução
    # ------------------------------------------------------------------

    def run(self, areas: List[AreaConfig], resources: ResourcePool) -> Dict:
        """
        Executa o ciclo completo de evolução do algoritmo genético.

        Retorna um dicionário com:
        - best_fitness: o maior valor de aptidão encontrado
        - generations: quantas gerações foram executadas
        - processing_time: tempo decorrido em segundos
        - allocations: lista de dicionários, um por área, com as contagens atribuídas
        - fitness_history: lista da melhor aptidão por geração (para gráficos)
        """
        start_time = time.time()
        num_areas = len(areas)

        if num_areas == 0:
            return {
                'best_fitness': 0.0,
                'generations': 0,
                'processing_time': 0.0,
                'allocations': [],
                'fitness_history': []
            }

        evaluator = FitnessEvaluator(areas, resources)
        population = self._initialize_population(num_areas)

        best_chromosome = None
        best_fitness = -1.0
        fitness_history = []
        stagnation_count = 0
        prev_best = -1.0

        for generation in range(self.max_generations):
            # Avaliar a aptidão de toda a população
            fitness_scores = [evaluator.evaluate(c) for c in population]

            # Monitorar a melhor solução encontrada até agora
            gen_best_idx = max(range(len(fitness_scores)), key=lambda i: fitness_scores[i])
            gen_best_fitness = fitness_scores[gen_best_idx]

            if gen_best_fitness > best_fitness:
                best_fitness = gen_best_fitness
                best_chromosome = copy.deepcopy(population[gen_best_idx])

            fitness_history.append(round(best_fitness, 4))

            # Parada antecipada: se não houver melhoria por 40 gerações, parar
            if abs(best_fitness - prev_best) < 0.0001:
                stagnation_count += 1
                if stagnation_count >= 40:
                    break
            else:
                stagnation_count = 0
            prev_best = best_fitness

            # --- Construir a próxima geração ---
            # Ordenar por aptidão (decrescente)
            sorted_pop = sorted(
                zip(population, fitness_scores),
                key=lambda x: x[1],
                reverse=True
            )

            next_population = []

            # Elitismo: manter os N melhores indivíduos sem alterações
            for i in range(self.elitism_count):
                next_population.append(copy.deepcopy(sorted_pop[i][0]))

            # Preencher o restante por meio de seleção, crossover e mutação
            pop_only = [item[0] for item in sorted_pop]
            scores_only = [item[1] for item in sorted_pop]

            while len(next_population) < self.population_size:
                parent1 = self._tournament_selection(pop_only, scores_only)
                parent2 = self._tournament_selection(pop_only, scores_only)
                child1, child2 = self._crossover(parent1, parent2)
                child1 = self._mutate(child1)
                child2 = self._mutate(child2)
                next_population.append(child1)
                if len(next_population) < self.population_size:
                    next_population.append(child2)

            population = next_population

        processing_time = time.time() - start_time
        total_generations = len(fitness_history)

        # Decodificar o melhor cromossomo em alocações legíveis
        allocations = []
        if best_chromosome:
            decoded = best_chromosome.decode(resources)
            for i, area in enumerate(areas):
                sec, fire, med = decoded[i]
                allocations.append({
                    'area_id': area.area_id,
                    'area_name': area.name,
                    'estimated_people': area.estimated_people,
                    'priority': area.priority,
                    'security': sec,
                    'firefighters': fire,
                    'medical': med
                })

        return {
            'best_fitness': round(best_fitness, 4),
            'generations': total_generations,
            'processing_time': round(processing_time, 3),
            'allocations': allocations,
            'fitness_history': fitness_history
        }
