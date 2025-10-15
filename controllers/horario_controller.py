import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from config.database import get_db_session
from controllers.user_controller import role_required  # Importa el decorador actualizado
from services.horario_service import HorarioService

# Inicializar servicio y Blueprint
service = HorarioService(get_db_session())
horario_bp = Blueprint('horario_bp', __name__)

# ---------------------------------------------------------------------
# GET - Listar todos los horarios
# ---------------------------------------------------------------------
@horario_bp.route('/horarios', methods=['GET'])
@jwt_required()
def get_horarios():
    logger.info("Consulta de todos los horarios")
    horarios = service.listar_horarios()
    return jsonify([
        {
            'id': h.id,
            'materia': h.materia,
            'docente': h.docente,
            'dia': h.dia,
            'hora_inicio': h.hora_inicio,
            'hora_fin': h.hora_fin,
            'salon': h.salon
        } for h in horarios
    ]), 200, {'Content-Type': 'application/json; charset=utf-8'}

# ---------------------------------------------------------------------
# GET - Obtener horario por ID
# ---------------------------------------------------------------------
@horario_bp.route('/horarios/<int:horario_id>', methods=['GET'])
@jwt_required()
def get_horario(horario_id):
    horario = service.obtener_horario(horario_id)
    if horario:
        logger.info(f"Consulta de horario por ID: {horario_id}")
        return jsonify({
            'id': horario.id,
            'materia': horario.materia,
            'docente': horario.docente,
            'dia': horario.dia,
            'hora_inicio': horario.hora_inicio,
            'hora_fin': horario.hora_fin,
            'salon': horario.salon
        }), 200, {'Content-Type': 'application/json; charset=utf-8'}
    logger.warning(f"Horario no encontrado: {horario_id}")
    return jsonify({'error': 'Horario no encontrado'}), 404, {'Content-Type': 'application/json; charset=utf-8'}

# ---------------------------------------------------------------------
# POST - Crear nuevo horario (solo admin)
# ---------------------------------------------------------------------
@horario_bp.route('/horarios', methods=['POST'])
@jwt_required()
@role_required('admin')
def create_horario():
    data = request.get_json()
    materia = data.get('materia')
    docente = data.get('docente')
    dia = data.get('dia')
    hora_inicio = data.get('hora_inicio')
    hora_fin = data.get('hora_fin')
    salon = data.get('salon')

    if not all([materia, docente, dia, hora_inicio, hora_fin, salon]):
        logger.warning("Intento de crear horario sin datos completos")
        return jsonify({'error': 'Todos los campos son obligatorios'}), 400, {'Content-Type': 'application/json; charset=utf-8'}

    horario = service.crear_horario(materia, docente, dia, hora_inicio, hora_fin, salon)
    logger.info(f"Horario creado: {materia} - {docente}")
    return jsonify({
        'id': horario.id,
        'materia': horario.materia,
        'docente': horario.docente,
        'dia': horario.dia,
        'hora_inicio': horario.hora_inicio,
        'hora_fin': horario.hora_fin,
        'salon': horario.salon
    }), 201, {'Content-Type': 'application/json; charset=utf-8'}

# ---------------------------------------------------------------------
# PUT - Actualizar horario (solo admin)
# ---------------------------------------------------------------------
@horario_bp.route('/horarios/<int:horario_id>', methods=['PUT'])
@role_required('admin')
def update_horario(horario_id):
    data = request.get_json()
    materia = data.get('materia')
    docente = data.get('docente')
    dia = data.get('dia')
    hora_inicio = data.get('hora_inicio')
    hora_fin = data.get('hora_fin')
    salon = data.get('salon')

    horario = service.actualizar_horario(horario_id, materia, docente, dia, hora_inicio, hora_fin, salon)
    if horario:
        logger.info(f"Horario actualizado: {horario_id}")
        return jsonify({
            'id': horario.id,
            'materia': horario.materia,
            'docente': horario.docente,
            'dia': horario.dia,
            'hora_inicio': horario.hora_inicio,
            'hora_fin': horario.hora_fin,
            'salon': horario.salon
        }), 200, {'Content-Type': 'application/json; charset=utf-8'}
    logger.warning(f"Horario no encontrado para actualizar: {horario_id}")
    return jsonify({'error': 'Horario no encontrado'}), 404, {'Content-Type': 'application/json; charset=utf-8'}

# ---------------------------------------------------------------------
# DELETE - Eliminar horario (solo admin)
# ---------------------------------------------------------------------
@horario_bp.route('/horarios/<int:horario_id>', methods=['DELETE'])
@role_required('admin')
def delete_horario(horario_id):
    horario = service.eliminar_horario(horario_id)
    if horario:
        logger.info(f"Horario eliminado: {horario_id}")
        return jsonify({'message': 'Horario eliminado correctamente'}), 200, {'Content-Type': 'application/json; charset=utf-8'}
    logger.warning(f"Horario no encontrado para eliminar: {horario_id}")
    return jsonify({'error': 'Horario no encontrado'}), 404, {'Content-Type': 'application/json; charset=utf-8'}
