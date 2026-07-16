"""Fábrica de la aplicación Flask (patrón app factory)."""
import os

from flask import Flask, jsonify, url_for

from app import db
from app.config import Config


def create_app(config_object=Config):
    app = Flask(__name__)
    app.config.from_object(config_object)

    # En Vercel (o cualquier entorno con la variable VERCEL definida), es
    # obligatorio configurar un JWT_SECRET propio: fallar rapido y con un
    # mensaje claro evita desplegar por error con el secreto de desarrollo.
    if os.getenv("VERCEL") and app.config["JWT_SECRET"] == "dev-secret-cambiar":
        raise RuntimeError(
            "JWT_SECRET no configurado. Define una variable de entorno "
            "JWT_SECRET segura en el proyecto de Vercel antes de desplegar."
        )

    # Cierre del cliente de BD por request.
    db.init_app(app)

    # --- Cache-busting de archivos estáticos (CSS/JS) ---
    # Los navegadores (sobre todo en móvil) pueden cachear agresivamente
    # styles.css/*.js. Añadimos "?v=<version>" para que, al cambiar el
    # contenido, la URL cambie y el navegador SIEMPRE traiga la version
    # nueva en vez de una copia obsoleta.
    #
    # En Vercel usamos el SHA del commit desplegado (estable durante toda
    # la vida de ese deployment, sin importar cuantas instancias/cold
    # starts lo sirvan). En local, usamos la fecha de modificacion de cada
    # archivo, para iterar rapido sin tener que limpiar cache a mano.
    deploy_version = os.getenv("VERCEL_GIT_COMMIT_SHA") or os.getenv("VERCEL_DEPLOYMENT_ID")

    @app.context_processor
    def inject_asset_url():
        def asset_url(filename):
            if deploy_version:
                version = deploy_version
            else:
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
