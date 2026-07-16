"""Fábrica de la aplicación Flask (patrón app factory)."""
import os

from flask import Flask, jsonify, url_for

from app import db
from app.config import Config


def create_app(config_object=Config):
    app = Flask(__name__)
    app.config.from_object(config_object)

    # Cierre del cliente de BD por request.
    db.init_app(app)

    # --- Cache-busting de archivos estáticos (CSS/JS) ---
    # Los navegadores (sobre todo en móvil) pueden cachear agresivamente
    # styles.css/*.js. Añadimos "?v=<fecha de modificación>" para que, al
    # editar un archivo, la URL cambie y el navegador SIEMPRE traiga la
    # versión nueva en vez de una copia obsoleta.
    @app.context_processor
    def inject_asset_url():
        def asset_url(filename):
            ruta = os.path.join(app.static_folder, filename)
            try:
                version = int(os.path.getmtime(ruta))
            except OSError:
                version = 0
            return f"{url_for('static', filename=filename)}?v={version}"

        return {"asset_url": asset_url}

    # --- Blueprints de la API (JSON) ---
    from app.api.auth_routes import bp as auth_bp
    from app.api.actividades_routes import bp as actividades_bp
    from app.api.admin_routes import bp as admin_bp
    from app.api.usuarios_routes import bp as usuarios_bp
    from app.api.tipos_routes import bp as tipos_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(actividades_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(usuarios_bp)
    app.register_blueprint(tipos_bp)

    # --- Blueprint de vistas (templates) ---
    from app.views.pages import bp as pages_bp

    app.register_blueprint(pages_bp)

    # --- Manejo uniforme de errores para rutas /api ---
    @app.errorhandler(404)
    def not_found(err):  # noqa: ARG001
        return jsonify({"error": "Recurso no encontrado"}), 404

    @app.errorhandler(405)
    def method_not_allowed(err):  # noqa: ARG001
        return jsonify({"error": "Método no permitido"}), 405

    @app.errorhandler(500)
    def server_error(err):  # noqa: ARG001
        return jsonify({"error": "Error interno del servidor"}), 500

    return app
