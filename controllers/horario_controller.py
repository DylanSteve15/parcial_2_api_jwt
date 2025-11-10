#controllers/horario_controller.py
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from config.database import get_db_session
from controllers.user_controller import role_required  # Importa el decorador actualizado
from services.horario_service import HorarioService
from services.user_service import UserService

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
    user_service = UserService(db)
    try:
        horarios = service.listar_horarios()
        resultado = []
        for h in horarios:
            usuario_email = 'Sin asignar'
            if h.user_id:
                try:
                    usuario = user_service.obtener_usuario_por_id(h.user_id)
                    usuario_email = usuario.email if usuario else 'Usuario eliminado'
                except Exception as e:
                    logger.warning(f"Error obteniendo usuario {h.user_id}: {str(e)}")
                    usuario_email = 'Error al obtener usuario'
            
            resultado.append({
                'id': h.id,
                'materia': h.materia,
                'docente': h.docente,
                'dia': h.dia,
                'hora_inicio': str(h.hora_inicio) if h.hora_inicio else None,
                'hora_fin': str(h.hora_fin) if h.hora_fin else None,
                'salon': h.salon,
                'user_id': h.user_id,
                'usuario': usuario_email
            })
        
        return jsonify(resultado), 200, {'Content-Type': 'application/json; charset=utf-8'}
    except Exception as e:
        logger.error(f"Error al obtener horarios: {str(e)}", exc_info=True)
        return jsonify({'error': f'Error al obtener horarios: {str(e)}'}), 500, {'Content-Type': 'application/json; charset=utf-8'}
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
        # Obtener horario actual para mantener su user_id
        horario_actual = service.obtener_horario(horario_id)
        if not horario_actual:
            logger.warning(f"Horario no encontrado para actualizar: {horario_id}")
            return jsonify({'error': 'Horario no encontrado'}), 404, {'Content-Type': 'application/json; charset=utf-8'}
        
        # Actualizar horario manteniendo el user_id existente
        horario = service.actualizar_horario(horario_id, materia, docente, dia, hora_inicio, hora_fin, salon, horario_actual.user_id)
        logger.info(f"Horario actualizado por admin: {horario_id}")
        return jsonify({
            'id': horario.id,
            'materia': horario.materia,
            'docente': horario.docente,
            'dia': horario.dia,
            'hora_inicio': str(horario.hora_inicio) if horario.hora_inicio else None,
            'hora_fin': str(horario.hora_fin) if horario.hora_fin else None,
            'salon': horario.salon,
            'user_id': horario.user_id
        }), 200, {'Content-Type': 'application/json; charset=utf-8'}
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


# =====================================================================
# 👤 RUTAS PARA USUARIOS (MIS HORARIOS - No requieren admin)
# =====================================================================

# GET - Listar mis horarios
# =====================================================================
@horario_bp.route('/mis-horarios', methods=['GET'])
@jwt_required()
def get_mis_horarios():
    """Obtiene todos los horarios del usuario autenticado"""
    current_user_id = get_jwt_identity()
    current_user_id = int(current_user_id) if isinstance(current_user_id, str) else current_user_id
    
    logger.info(f"Usuario {current_user_id} consultando sus horarios")
    db = next(get_db_session())
    service = HorarioService(db)
    try:
        horarios = service.obtener_horarios_por_usuario(current_user_id)
        return jsonify([
            {
                'id': h.id,
                'materia': h.materia,
                'docente': h.docente,
                'dia': h.dia,
                'hora_inicio': str(h.hora_inicio) if h.hora_inicio else None,
                'hora_fin': str(h.hora_fin) if h.hora_fin else None,
                'salon': h.salon,
                'user_id': h.user_id
            } for h in horarios
        ]), 200, {'Content-Type': 'application/json; charset=utf-8'}
    finally:
        db.close()


# POST - Crear mi horario
# =====================================================================
@horario_bp.route('/mis-horarios', methods=['POST'])
@jwt_required()
def create_mi_horario():
    """Crea un horario para el usuario autenticado"""
    current_user_id = get_jwt_identity()
    current_user_id = int(current_user_id) if isinstance(current_user_id, str) else current_user_id
    
    data = request.get_json()
    materia = data.get('materia')
    docente = data.get('docente')
    dia = data.get('dia')
    hora_inicio = data.get('hora_inicio')
    hora_fin = data.get('hora_fin')
    salon = data.get('salon')

    if not all([materia, docente, dia, hora_inicio, hora_fin, salon]):
        logger.warning(f"Usuario {current_user_id} intenta crear horario sin datos completos")
        return jsonify({'error': 'Todos los campos son obligatorios'}), 400, {'Content-Type': 'application/json; charset=utf-8'}

    db = next(get_db_session())
    service = HorarioService(db)
    try:
        # Crear horario asignado al usuario actual
        horario = service.crear_horario(materia, docente, dia, hora_inicio, hora_fin, salon, current_user_id)
        logger.info(f"Horario creado por usuario {current_user_id}: {materia} - {docente}")
        return jsonify({
            'id': horario.id,
            'materia': horario.materia,
            'docente': horario.docente,
            'dia': horario.dia,
            'hora_inicio': str(horario.hora_inicio) if horario.hora_inicio else None,
            'hora_fin': str(horario.hora_fin) if horario.hora_fin else None,
            'salon': horario.salon,
            'user_id': horario.user_id
        }), 201, {'Content-Type': 'application/json; charset=utf-8'}
    except Exception as e:
        logger.error(f"Error al crear horario para usuario {current_user_id}: {str(e)}", exc_info=True)
        db.rollback()
        return jsonify({'error': f'Error al crear horario: {str(e)}'}), 500, {'Content-Type': 'application/json; charset=utf-8'}
    finally:
        db.close()


# PUT - Editar mi horario
# =====================================================================
@horario_bp.route('/mis-horarios/<int:horario_id>', methods=['PUT'])
@jwt_required()
def update_mi_horario(horario_id):
    """Edita un horario del usuario autenticado"""
    current_user_id = get_jwt_identity()
    current_user_id = int(current_user_id) if isinstance(current_user_id, str) else current_user_id
    
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
        # Verificar que el horario pertenece al usuario actual
        horario = service.obtener_horario(horario_id)
        if not horario:
            logger.warning(f"Horario no encontrado: {horario_id}")
            return jsonify({'error': 'Horario no encontrado'}), 404, {'Content-Type': 'application/json; charset=utf-8'}
        
        if horario.user_id != current_user_id:
            logger.warning(f"Usuario {current_user_id} intenta editar horario ajeno {horario_id}")
            return jsonify({'error': 'No tienes permiso para editar este horario'}), 403, {'Content-Type': 'application/json; charset=utf-8'}
        
        # Actualizar horario manteniendo el user_id
        horario_actualizado = service.actualizar_horario(horario_id, materia, docente, dia, hora_inicio, hora_fin, salon, current_user_id)
        logger.info(f"Horario {horario_id} actualizado por usuario {current_user_id}")
        return jsonify({
            'id': horario_actualizado.id,
            'materia': horario_actualizado.materia,
            'docente': horario_actualizado.docente,
            'dia': horario_actualizado.dia,
            'hora_inicio': str(horario_actualizado.hora_inicio) if horario_actualizado.hora_inicio else None,
            'hora_fin': str(horario_actualizado.hora_fin) if horario_actualizado.hora_fin else None,
            'salon': horario_actualizado.salon,
            'user_id': horario_actualizado.user_id
        }), 200, {'Content-Type': 'application/json; charset=utf-8'}
    finally:
        db.close()


# DELETE - Eliminar mi horario
# =====================================================================
@horario_bp.route('/mis-horarios/<int:horario_id>', methods=['DELETE'])
@jwt_required()
def delete_mi_horario(horario_id):
    """Elimina un horario del usuario autenticado"""
    current_user_id = get_jwt_identity()
    current_user_id = int(current_user_id) if isinstance(current_user_id, str) else current_user_id
    
    db = next(get_db_session())
    service = HorarioService(db)
    try:
        # Verificar que el horario pertenece al usuario actual
        horario = service.obtener_horario(horario_id)
        if not horario:
            logger.warning(f"Horario no encontrado: {horario_id}")
            return jsonify({'error': 'Horario no encontrado'}), 404, {'Content-Type': 'application/json; charset=utf-8'}
        
        if horario.user_id != current_user_id:
            logger.warning(f"Usuario {current_user_id} intenta eliminar horario ajeno {horario_id}")
            return jsonify({'error': 'No tienes permiso para eliminar este horario'}), 403, {'Content-Type': 'application/json; charset=utf-8'}
        
        # Eliminar horario
        service.eliminar_horario(horario_id)
        logger.info(f"Horario {horario_id} eliminado por usuario {current_user_id}")
        return jsonify({'message': 'Horario eliminado correctamente'}), 200, {'Content-Type': 'application/json; charset=utf-8'}
    finally:
        db.close()
