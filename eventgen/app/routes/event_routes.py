from flask import Blueprint, render_template, request, redirect, url_for, flash
from ..models.event_model import Event
from ..models.area_model import Area
from ..models.optimization_model import Optimization

event_bp = Blueprint('events', __name__)


@event_bp.route('/')
def index():
    events = Event.get_all()
    return render_template('index.html', events=events)


@event_bp.route('/events/new', methods=['GET', 'POST'])
def new_event():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        total_participants = int(request.form.get('total_participants', 0))
        security_count = int(request.form.get('security_count', 0))
        firefighter_count = int(request.form.get('firefighter_count', 0))
        medical_count = int(request.form.get('medical_count', 0))

        if not name or total_participants <= 0:
            flash('Nome e quantidade de participantes são obrigatórios.', 'danger')
            return render_template('event_form.html')

        event_id = Event.create(name, total_participants, security_count,
                                firefighter_count, medical_count)
        flash('Evento cadastrado com sucesso.', 'success')
        return redirect(url_for('events.event_detail', event_id=event_id))

    return render_template('event_form.html')


@event_bp.route('/events/<int:event_id>')
def event_detail(event_id):
    event = Event.get_by_id(event_id)
    if not event:
        flash('Evento não encontrado.', 'danger')
        return redirect(url_for('events.index'))

    areas = Area.get_by_event(event_id)
    optimization = Optimization.get_by_event(event_id)
    return render_template('event_detail.html', event=event, areas=areas, optimization=optimization)


@event_bp.route('/events/<int:event_id>/delete', methods=['POST'])
def delete_event(event_id):
    Event.delete(event_id)
    flash('Evento removido com sucesso.', 'success')
    return redirect(url_for('events.index'))
