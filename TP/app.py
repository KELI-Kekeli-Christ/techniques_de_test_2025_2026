"""
Implémentation du serveur Flask pour le service Triangulator.

Définit les endpoints de l'API, gère les appels au PointSetManager
et orchestre la logique de triangulation.
"""

import uuid
import logging
from flask import Flask, jsonify, Response, abort
from services import logic
from services import serialization

# Configuration du logging
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

app = Flask(__name__)

POINT_SET_MANAGER_URL = "http://localhost:5000"  

@app.route("/triangulation/<pointSetId>", methods=["GET"])
def get_triangulation(pointSetId: str):
    """
    Endpoint principal pour obtenir la triangulation.
    
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
        # Gère le cas d'un format d'ID invalide (Erreur 400) [cite: triangulator.yml]
        log.warning(f"Format UUID invalide: {pointSetId}")
        abort(400, description="Le PointSetID n'est pas un UUID valide.")

    log.warning("Logique non implémentée (Rendu 2).")
    raise NotImplementedError("Logique non implémentée pour le Rendu 2.")


# --- Gestion d'erreurs JSON ---

@app.errorhandler(400)
def bad_request(error):
    """Handler pour 400 Bad Request."""
    return jsonify({
        "code": "BAD_REQUEST",
        "message": error.description or "Requête invalide."
    }), 400

@app.errorhandler(404)
def not_found(error):
    """Handler pour 404 Not Found."""
    return jsonify({
        "code": "NOT_FOUND",
        "message": error.description or "Ressource non trouvée."
    }), 404

@app.errorhandler(503)
def service_unavailable(error):
    """Handler pour 503 Service Unavailable."""
    return jsonify({
        "code": "SERVICE_UNAVAILABLE",
        "message": error.description or "Un service externe est indisponible."
    }), 503

@app.errorhandler(NotImplementedError)
def not_implemented(error):
    """Handler pour 500 si la logique n'est pas faite (Rendu 2)."""
    return jsonify({
        "code": "NOT_IMPLEMENTED",
        "message": str(error) or "Fonctionnalité non implémentée."
    }), 500

@app.errorhandler(500)
def internal_error(error):
    """Handler générique pour 500 Internal Server Error."""
    return jsonify({
        "code": "INTERNAL_ERROR",
        "message": error.description or "Erreur interne du serveur."
    }), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
