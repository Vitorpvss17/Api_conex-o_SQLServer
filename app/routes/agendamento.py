from flask import Blueprint, request, jsonify, current_app
from app.database.database import get_connection

# Inicialização do blueprint
agendamento_bp = Blueprint('agendamento', __name__)

@agendamento_bp.route('/', methods=['GET'])
def listar_agendamento():
    cliente_id = request.args.get('clienteId')
    try:
        current_app.logger.info(f"Tentando listar agendamentos para o cliente ID: {cliente_id}")
        conn = get_connection()
        cursor = conn.cursor()

        # Consulta para buscar agendamentos do cliente
        cursor.execute("SELECT id, clienteId, data, servico FROM agendamento WHERE clienteId = ?", (cliente_id,))
        rows = cursor.fetchall()

        # Formata os agendamentos para o JSON de resposta
        agendamentos = [
            {
                'id': row[0],
                'clienteId': row[1],
                'data': row[2].strftime('%Y-%m-%d %H:%M:%S'),  # Formatar data e hora
                'servico': row[3],
            }
            for row in rows
        ]

        current_app.logger.info(f"Agendamentos encontrados: {len(agendamentos)}")
        return jsonify(agendamentos), 200
    except Exception as e:
        current_app.logger.error(f"Erro ao listar agendamentos: {e}")
        return jsonify({'error': 'Erro ao listar agendamentos.', 'details': str(e)}), 500
    finally:
        if 'conn' in locals():
            conn.close()

@agendamento_bp.route('/', methods=['POST'])
def criar_agendamento():
    try:
        data = request.json
        current_app.logger.info(f"Dados recebidos para criação de agendamento: {data}")

        # Validação de campos obrigatórios
        cliente_id = data.get('clienteId')
        data_agendamento = data.get('data')
        servico = data.get('servico')

        if not all([cliente_id, data_agendamento, servico]):
            current_app.logger.warning("Campos obrigatórios ausentes na solicitação.")
            return jsonify({'error': 'Todos os campos obrigatórios devem ser preenchidos.'}), 400

        # Inserir dados no banco de dados
        current_app.logger.info("Tentando conectar ao banco de dados...")
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO agendamento (clienteId, data, servico)
            VALUES (?, ?, ?)
            """,
            (cliente_id, data_agendamento, servico)
        )
        conn.commit()
        current_app.logger.info("Agendamento criado com sucesso no banco de dados.")

        return jsonify({'message': 'Agendamento criado com sucesso!'}), 201
    except Exception as e:
        current_app.logger.error(f"Erro ao criar agendamento: {e}")
        return jsonify({'error': 'Erro ao criar agendamento.', 'details': str(e)}), 500
    finally:
        if 'conn' in locals():
            conn.close()

@agendamento_bp.route('/<int:id>', methods=['DELETE'])
def excluir_agendamento(id):
    try:
        current_app.logger.info(f"Tentando excluir agendamento com ID: {id}")
        conn = get_connection()
        cursor = conn.cursor()

        # Verificar se o agendamento existe
        cursor.execute("SELECT id FROM agendamento WHERE id = ?", (id,))
        row = cursor.fetchone()

        if not row:
            current_app.logger.warning(f"Nenhum agendamento encontrado com ID: {id}")
            return jsonify({'error': 'Agendamento não encontrado.'}), 404

        # Excluir o agendamento
        cursor.execute("DELETE FROM agendamento WHERE id = ?", (id,))
        conn.commit()
        current_app.logger.info(f"Agendamento com ID {id} excluído com sucesso.")

        return jsonify({'message': 'Agendamento excluído com sucesso!'}), 200
    except Exception as e:
        current_app.logger.error(f"Erro ao excluir agendamento: {e}")
        return jsonify({'error': 'Erro ao excluir agendamento.', 'details': str(e)}), 500
    finally:
        if 'conn' in locals():
            conn.close()