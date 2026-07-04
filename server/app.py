# from __future__ import annotations

# from flask import Flask, jsonify

# def create_app() -> Flask:
#     app = Flask(__name__)

#     @app.route("/api/health")
#     def health():
#         return jsonify({"status" : "ok"})
    
#     return app

#==================================================================
#==================================================================
#==================================================================

from __future__ import annotations

from flask import Flask, jsonify

from server.config import Config

def create_app(test_config: dict | None = None) -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

    if test_config:
        app.config.update(test_config)
    
    @app.route("/api/health")
    def health():
        return jsonify(
            {
                "status" : "ok",
                "host" : app.config["APP_HOST"],
                "port" : app.config["APP_PORT"]
            }
        )

    return app