"""Implémentation du serveur Flask pour le service Triangulator.

Définit les endpoints de l'API, gère les appels au PointSetManager
et orchestre la logique de triangulation.
"""

import logging
import uuid

import requests
from flask import Flask, Response, abort, jsonify
from triangulator.logic import compute_triangulation
from triangulator.serialization import parse_pointset_binary, serialize_triangles_binary

# Configuration du logging
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

app = Flask(__name__)

POINT_SET_MANAGER_URL = "http://localhost:5001"


@app.route("/triangulation/<pointSetId>", methods=["GET"])
def get_triangulation(pointSetId: str):
    """Endpoint principal pour obtenir la triangulation.
    
    Récupère le PointSet du PointSetManager, calcule la triangulation, 
    et renvoie le résultat en binaire.
    
    Args:
        pointSetId: L'ID (UUID) du PointSet à trianguler.
        
    Returns:
        Une Réponse Flask. Soit les Triangles en binaire (200),
        soit une erreur JSON (400, 500 , etc).

    """
    log.debug(f"Requête reçue pour pointSetId: {pointSetId}")
    
    # 1. Valider le format de l'UUID
    try:
        point_set_uuid = uuid.UUID(pointSetId)
        log.debug(f"UUID validé: {point_set_uuid}")
    except ValueError:
        # Gère le cas d'un format d'ID invalide (Erreur 400)
        log.warning(f"Format UUID invalide: {pointSetId}")
        abort(400, description="Le PointSetID n'est pas un UUID valide.")

    # 2. Récupérer le PointSet depuis le PointSetManager
    try:
        pointset_url = f"{POINT_SET_MANAGER_URL}/pointset/{pointSetId}"
        log.debug(f"Récupération du PointSet depuis: {pointset_url}")
        
        response = requests.get(pointset_url, timeout=10)
        
        if response.status_code == 404:
            log.warning(f"PointSet non trouvé: {pointSetId}")
            abort(404, description="Le PointSet spécifié n'a pas été trouvé.")
        
        if response.status_code == 400:
            log.warning(f"Requête invalide vers PointSetManager: {pointSetId}")
            abort(400, description="Requête invalide vers le PointSetManager.")
        
        if response.status_code != 200:
            log.error(
                f"Erreur du PointSetManager (status {response.status_code}): "
                f"{pointSetId}"
            )
            abort(503, description="Le PointSetManager est indisponible.")
        
        pointset_binary = response.content
        log.debug(f"PointSet récupéré: {len(pointset_binary)} bytes")
        
    except requests.exceptions.ConnectionError:
        log.error(f"Impossible de se connecter au PointSetManager: {pointSetId}")
        abort(503, description="Impossible de se connecter au PointSetManager.")
    except requests.exceptions.Timeout:
        log.error(f"Timeout lors de la connexion au PointSetManager: {pointSetId}")
        abort(503, description="Timeout lors de la connexion au PointSetManager.")
    except requests.exceptions.RequestException as e:
        log.error(f"Erreur de requête vers PointSetManager: {e}")
        abort(503, description="Erreur de communication avec le PointSetManager.")

    # 3. Parser les données binaires
    try:
        points = parse_pointset_binary(pointset_binary)
        log.debug(f"PointSet parsé: {len(points)} points")
    except ValueError as e:
        log.error(f"Erreur lors du parsing du PointSet: {e}")
        abort(500, description="Format de données PointSet invalide.")

    # 4. Calculer la triangulation
    try:
        triangles = compute_triangulation(points)
        log.debug(f"Triangulation calculée: {len(triangles)} triangles")
    except ValueError as e:
        log.error(f"Erreur lors de la triangulation: {e}")
        abort(500, description=f"Erreur lors de la triangulation: {str(e)}")
    except Exception as e:
        log.error(f"Erreur inattendue lors de la triangulation: {e}")
        abort(500, description="Erreur interne lors du calcul de la triangulation.")

    # 5. Sérialiser le résultat
    try:
        triangles_binary = serialize_triangles_binary(points, triangles)
        log.debug(f"Triangles sérialisés: {len(triangles_binary)} bytes")
    except ValueError as e:
        log.error(f"Erreur lors de la sérialisation: {e}")
        abort(500, description="Erreur lors de la sérialisation des triangles.")

    # 6. Renvoyer la réponse
    return Response(
        triangles_binary,
        mimetype='application/octet-stream',
        status=200
    )


# --- Gestion d'erreurs JSON ---
@app.errorhandler(400)
def bad_request(error):
    """Handle 400 Bad Request errors."""
    return jsonify({
        "code": "BAD_REQUEST",
        "message": error.description or "Requête invalide."
    }), 400

@app.errorhandler(404)
def not_found(error):
    """Handle 404 Not Found errors."""
    return jsonify({
        "code": "NOT_FOUND",
        "message": error.description or "Ressource non trouvée."
    }), 404

@app.errorhandler(503)
def service_unavailable(error):
    """Handle 503 Service Unavailable errors."""
    return jsonify({
        "code": "SERVICE_UNAVAILABLE",
        "message": error.description or "Un service externe est indisponible."
    }), 503

@app.errorhandler(NotImplementedError)
def not_implemented(error):
    """Handle 500 errors when functionality is not implemented."""
    return jsonify({
        "code": "NOT_IMPLEMENTED",
        "message": str(error) or "Fonctionnalité non implémentée."
    }), 500

@app.errorhandler(500)
def internal_error(error):
    """Handle generic 500 Internal Server Error responses."""
    return jsonify({
        "code": "INTERNAL_ERROR",
        "message": error.description or "Erreur interne du serveur."
    }), 500



