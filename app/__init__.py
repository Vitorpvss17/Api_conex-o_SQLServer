from flask import Flask
from flask_cors import CORS
from app.routes.clientes import clientes_bp
from app.routes.receita import receita_bp
from app.routes.procedimento import procedimento_bp
from app.routes.agendamento import agendamento_bp

def create_app():
    app = Flask(__name__)
    CORS(app, resources={
        r"/clientes/*": {"origins": "*"},  # Permite todas as origens (ajuste para produção)
        r"/receitas/*": {"origins": "*"},
        r"/procedimento/*": {"origins": "*"},
        r"/agendamento/*": {"origins": "*"}
    })

    # Registro de blueprints
    app.register_blueprint(clientes_bp, url_prefix='/clientes')
    app.register_blueprint(receita_bp, url_prefix='/receitas')
    app.register_blueprint(procedimento_bp, url_prefix='/procedimento')
    app.register_blueprint(agendamento_bp, url_prefix='/agendamento')

    return app