#controllers/horario_controller.py
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from config.database import get_db_session
from controllers.user_controller import role_required  # Importa el decorador actualizado
from services.horario_service import HorarioService

# Inicializar Blueprint
horario_bp = Blueprint('horario_bp', __name__)

# ---------------------------------------------------------------------
# GET - Listar todos los horarios
# ---------------------------------------------------------------------
@horario_bp.route('/horarios', methods=['GET'])
@jwt_required()
def get_horarios():
    logger.info("Consulta de todos los horarios")
    # Log del header de autorización para debugging
    auth_header = request.headers.get('Authorization', 'No header')
    logger.info(f"Authorization header recibido: {auth_header[:50] if len(auth_header) > 50 else auth_header}...")
    db = next(get_db_session())
    service = HorarioService(db)
    try:
        horarios = service.listar_horarios()
        return jsonify([
            {
                'id': h.id,
                'materia': h.materia,
                'docente': h.docente,
                'dia': h.dia,
                'hora_inicio': str(h.hora_inicio) if h.hora_inicio else None,
                'hora_fin': str(h.hora_fin) if h.hora_fin else None,
                'salon': h.salon
            } for h in horarios
        ]), 200, {'Content-Type': 'application/json; charset=utf-8'}
    finally:
        db.close()

# ---------------------------------------------------------------------
# GET - Obtener horario por ID
# ---------------------------------------------------------------------
@horario_bp.route('/horarios/<int:horario_id>', methods=['GET'])
@jwt_required()
def get_horario(horario_id):
    db = next(get_db_session())
    service = HorarioService(db)
    try:
        horario = service.obtener_horario(horario_id)
        if horario:
            logger.info(f"Consulta de horario por ID: {horario_id}")
            return jsonify({
                'id': horario.id,
                'materia': horario.materia,
                'docente': horario.docente,
                'dia': horario.dia,
                'hora_inicio': str(horario.hora_inicio) if horario.hora_inicio else None,
                'hora_fin': str(horario.hora_fin) if horario.hora_fin else None,
                'salon': horario.salon
            }), 200, {'Content-Type': 'application/json; charset=utf-8'}
        logger.warning(f"Horario no encontrado: {horario_id}")
        return jsonify({'error': 'Horario no encontrado'}), 404, {'Content-Type': 'application/json; charset=utf-8'}
    finally:
        db.close()

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

    db = next(get_db_session())
    service = HorarioService(db)
    try:
        # Crear horario sin asignar usuario (user_id será None)
        horario = service.crear_horario(materia, docente, dia, hora_inicio, hora_fin, salon, None)
        logger.info(f"Horario creado: {materia} - {docente}")
        return jsonify({
            'id': horario.id,
            'materia': horario.materia,
            'docente': horario.docente,
            'dia': horario.dia,
            'hora_inicio': str(horario.hora_inicio) if horario.hora_inicio else None,
            'hora_fin': str(horario.hora_fin) if horario.hora_fin else None,
            'salon': horario.salon
        }), 201, {'Content-Type': 'application/json; charset=utf-8'}
    except Exception as e:
        logger.error(f"Error al crear horario: {str(e)}", exc_info=True)
        db.rollback()
        return jsonify({'error': f'Error al crear horario: {str(e)}'}), 500, {'Content-Type': 'application/json; charset=utf-8'}
    finally:
        db.close()

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

    db = next(get_db_session())
    service = HorarioService(db)
    try:
        # Actualizar horario sin cambiar user_id (mantiene el valor existente o None)
        horario = service.actualizar_horario(horario_id, materia, docente, dia, hora_inicio, hora_fin, salon, None)
        if horario:
            logger.info(f"Horario actualizado: {horario_id}")
            return jsonify({
                'id': horario.id,
                'materia': horario.materia,
                'docente': horario.docente,
                'dia': horario.dia,
                'hora_inicio': str(horario.hora_inicio) if horario.hora_inicio else None,
                'hora_fin': str(horario.hora_fin) if horario.hora_fin else None,
                'salon': horario.salon
            }), 200, {'Content-Type': 'application/json; charset=utf-8'}
        logger.warning(f"Horario no encontrado para actualizar: {horario_id}")
        return jsonify({'error': 'Horario no encontrado'}), 404, {'Content-Type': 'application/json; charset=utf-8'}
    finally:
        db.close()

# ---------------------------------------------------------------------
# DELETE - Eliminar horario (solo admin)
# ---------------------------------------------------------------------
@horario_bp.route('/horarios/<int:horario_id>', methods=['DELETE'])
@role_required('admin')
def delete_horario(horario_id):
    db = next(get_db_session())
    service = HorarioService(db)
    try:
        horario = service.eliminar_horario(horario_id)
        if horario:
            logger.info(f"Horario eliminado: {horario_id}")
            return jsonify({'message': 'Horario eliminado correctamente'}), 200, {'Content-Type': 'application/json; charset=utf-8'}
        logger.warning(f"Horario no encontrado para eliminar: {horario_id}")
        return jsonify({'error': 'Horario no encontrado'}), 404, {'Content-Type': 'application/json; charset=utf-8'}
    finally:
        db.close()
