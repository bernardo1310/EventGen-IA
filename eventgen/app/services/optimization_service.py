from ..services.genetic_algorithm import GeneticAlgorithm, AreaConfig, ResourcePool
from ..models.area_model import Area
from ..models.event_model import Event
from ..models.optimization_model import Optimization


class OptimizationService:

    @staticmethod
    def run_optimization(event_id: int) -> dict:
        event = Event.get_by_id(event_id)
        if not event:
            raise ValueError(f'Event {event_id} not found')

        areas_rows = Area.get_by_event(event_id)
        if not areas_rows:
            raise ValueError('No areas registered for this event')

        areas = [
            AreaConfig(
                area_id=row['id'],
                name=row['name'],
                estimated_people=row['estimated_people'],
                priority=row['priority']
            )
            for row in areas_rows
        ]

        resources = ResourcePool(
            security=event['security_count'],
            firefighters=event['firefighter_count'],
            medical=event['medical_count']
        )

        ga = GeneticAlgorithm(
            population_size=80,
            max_generations=200,
            crossover_rate=0.85,
            mutation_rate=0.15,
            elitism_count=4,
            tournament_size=5
        )

        result = ga.run(areas, resources)

        Optimization.save(
            event_id=event_id,
            best_fitness=result['best_fitness'],
            generations=result['generations'],
            processing_time=result['processing_time'],
            result_data=result
        )

        return result
