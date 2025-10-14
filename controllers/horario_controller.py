import logging
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from services.horario_service import HorarioService
from config.database import get_db_session

# Configuración del logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Definición del Blueprint para las rutas de horarios
horario_bp = Blueprint('horario_bp', __name__)

# Instancia del servicio (en entorno real se maneja por request context)
service = HorarioService(get_db_session())


@horario_bp.route('/horarios', methods=['GET'])
@jwt_required()
def listar_horarios():
    """
    GET /horarios
    Recupera todos los horarios registrados en el sistema.
    Retorna una lista JSON con los horarios disponibles.
    """
    logger.info("Consulta de todos los horarios")
    horarios = service.listar_horarios()
    return jsonify([
        {
            'id': h.id,
            'materia': h.materia,
            'docente': h.docente,
            'hora_inicio': h.hora_inicio,
            'hora_fin': h.hora_fin,
            'dia': h.dia
        } for h in horarios
    ]), 200


@horario_bp.route('/horarios/<int:horario_id>', methods=['GET'])
@jwt_required()
def obtener_horario(horario_id):
    """
    GET /horarios/<horario_id>
    Recupera un horario específico por su ID.
    """
    logger.info(f"Consultando horario con ID: {horario_id}")
    horario = service.obtener_horario(horario_id)
    if horario:
        return jsonify({
            'id': horario.id,
            'materia': horario.materia,
            'docente': horario.docente,
            'hora_inicio': horario.hora_inicio,
            'hora_fin': horario.hora_fin,
            'dia': horario.dia
        }), 200
    logger.warning(f"Horario no encontrado: {horario_id}")
    return jsonify({'error': 'Horario no encontrado'}), 404


@horario_bp.route('/horarios', methods=['POST'])
@jwt_required()
def crear_horario():
    """
    POST /horarios
    Crea un nuevo horario en el sistema.
    Cuerpo JSON esperado:
    {
        "materia": "Matemáticas",
        "docente": "Juan Pérez",
        "hora_inicio": "08:00",
        "hora_fin": "10:00",
        "dia": "Lunes"
    }
    """
    data = request.get_json()
    campos = ['materia', 'docente', 'hora_inicio', 'hora_fin', 'dia']
    
    # Validar campos requeridos
    if not all(campo in data and data[campo] for campo in campos):
        logger.warning("Intento de crear horario con campos incompletos")
        return jsonify({'error': 'Todos los campos son obligatorios'}), 400

    horario = service.crear_horario(**data)
    logger.info(f"Horario creado para la materia: {data['materia']}")
    return jsonify({
        'id': horario.id,
        'materia': horario.materia,
        'docente': horario.docente,
        'hora_inicio': horario.hora_inicio,
        'hora_fin': horario.hora_fin,
        'dia': horario.dia
    }), 201


@horario_bp.route('/horarios/<int:horario_id>', methods=['PUT'])
@jwt_required()
def actualizar_horario(horario_id):
    """
    PUT /horarios/<horario_id>
    Actualiza los datos de un horario existente.
    """
    data = request.get_json()
    logger.info(f"Actualizando horario con ID: {horario_id}")
    horario = service.actualizar_horario(horario_id, **data)
    if horario:
        return jsonify({
            'id': horario.id,
            'materia': horario.materia,
            'docente': horario.docente,
            'hora_inicio': horario.hora_inicio,
            'hora_fin': horario.hora_fin,
            'dia': horario.dia
        }), 200
    logger.warning(f"Horario no encontrado para actualizar: {horario_id}")
    return jsonify({'error': 'Horario no encontrado'}), 404


@horario_bp.route('/horarios/<int:horario_id>', methods=['DELETE'])
@jwt_required()
def eliminar_horario(horario_id):
    """
    DELETE /horarios/<horario_id>
    Elimina un horario por su ID.
    """
    logger.info(f"Intentando eliminar horario con ID: {horario_id}")
    eliminado = service.eliminar_horario(horario_id)
    if eliminado:
        return jsonify({'message': 'Horario eliminado correctamente'}), 200
    logger.warning(f"No se encontró horario para eliminar: {horario_id}")
    return jsonify({'error': 'Horario no encontrado'}), 404
