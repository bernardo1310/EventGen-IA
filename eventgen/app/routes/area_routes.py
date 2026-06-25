from flask import Blueprint, request, redirect, url_for, flash
from ..models.area_model import Area
from ..models.event_model import Event

area_bp = Blueprint('areas', __name__)


@area_bp.route('/events/<int:event_id>/areas/new', methods=['POST'])
def new_area(event_id):
    event = Event.get_by_id(event_id)
    if not event:
        flash('Evento não encontrado.', 'danger')
        return redirect(url_for('events.index'))

    name = request.form.get('name', '').strip()
    estimated_people = int(request.form.get('estimated_people', 0))
    priority = request.form.get('priority', 'Media')

    if not name or estimated_people <= 0:
        flash('Nome e público estimado são obrigatórios.', 'danger')
        return redirect(url_for('events.event_detail', event_id=event_id))

    if priority not in Area.PRIORITIES:
        flash('Prioridade inválida.', 'danger')
        return redirect(url_for('events.event_detail', event_id=event_id))

    Area.create(event_id, name, estimated_people, priority)
    flash('Área cadastrada com sucesso.', 'success')
    return redirect(url_for('events.event_detail', event_id=event_id))


@area_bp.route('/areas/<int:area_id>/delete', methods=['POST'])
def delete_area(area_id):
    area = Area.get_by_id(area_id)
    if not area:
        flash('Área não encontrada.', 'danger')
        return redirect(url_for('events.index'))

    event_id = area['event_id']
    Area.delete(area_id)
    flash('Área removida com sucesso.', 'success')
    return redirect(url_for('events.event_detail', event_id=event_id))
