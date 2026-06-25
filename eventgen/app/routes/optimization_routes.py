from flask import Blueprint, redirect, url_for, flash, jsonify
from ..services.optimization_service import OptimizationService

optimization_bp = Blueprint('optimization', __name__)


@optimization_bp.route('/events/<int:event_id>/optimize', methods=['POST'])
def run_optimization(event_id):
    try:
        result = OptimizationService.run_optimization(event_id)
        flash('Otimização concluída com sucesso.', 'success')
    except ValueError as e:
        flash(str(e), 'danger')

    return redirect(url_for('events.event_detail', event_id=event_id))
