from flask import Blueprint, request, jsonify, current_app
from app.database.database import get_connection

# Inicialização do blueprint
procedimento_bp = Blueprint('procedimento', __name__)

@procedimento_bp.route('/', methods=['GET'])
def listar_procedimentos():
    cliente_id = request.args.get('clienteId')
    try:
        current_app.logger.info(f"Tentando listar procedimentos para o cliente ID: {cliente_id}")
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT id, clienteId, data, descricao, titulo, valor FROM Procedimento WHERE clienteId = ?", (cliente_id,))
        rows = cursor.fetchall()

        procedimentos = [
            {
                'id': row[0],
                'clienteId': row[1],
                'data': row[2].strftime('%Y-%m-%d'),  # Formatar data
                'descricao': row[3],
                'titulo': row[4],
                'valor': float(row[5])  # Converter para float
            }
            for row in rows
        ]

        current_app.logger.info(f"Procedimentos encontrados: {len(procedimentos)}")
        return jsonify(procedimentos), 200
    except Exception as e:
        current_app.logger.error(f"Erro ao listar procedimentos: {e}")
        return jsonify({'error': 'Erro ao listar procedimentos.', 'details': str(e)}), 500
    finally:
        if 'conn' in locals():
            conn.close()

@procedimento_bp.route('/', methods=['POST'])
def criar_procedimento():
    try:
        data = request.json
        current_app.logger.info(f"Dados recebidos para criação de procedimento: {data}")

        # Validação de campos obrigatórios
        cliente_id = data.get('clienteId')
        data_procedimento = data.get('data')
        descricao = data.get('descricao')
        titulo = data.get('titulo')
        valor = data.get('valor')

        if not all([cliente_id, data_procedimento, descricao, titulo, valor]):
            current_app.logger.warning("Campos obrigatórios ausentes na solicitação.")
            return jsonify({'error': 'Todos os campos obrigatórios devem ser preenchidos.'}), 400

        # Inserir dados no banco de dados
        current_app.logger.info("Tentando conectar ao banco de dados...")
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO Procedimento (clienteId, data, descricao, titulo, valor)
            VALUES (?, ?, ?, ?, ?)
            """,
            (cliente_id, data_procedimento, descricao, titulo, valor)
        )
        conn.commit()
        current_app.logger.info("Procedimento criado com sucesso no banco de dados.")

        return jsonify({'message': 'Procedimento criado com sucesso!'}), 201
    except Exception as e:
        current_app.logger.error(f"Erro ao criar procedimento: {e}")
        return jsonify({'error': 'Erro ao criar procedimento.', 'details': str(e)}), 500
    finally:
        if 'conn' in locals():
            conn.close()

@procedimento_bp.route('/<int:id>', methods=['DELETE'])
def excluir_procedimento(id):
    try:
        current_app.logger.info(f"Tentando excluir procedimento com ID: {id}")
        conn = get_connection()
        cursor = conn.cursor()

        # Verificar se o procedimento existe
        cursor.execute("SELECT id FROM Procedimento WHERE id = ?", (id,))
        row = cursor.fetchone()

        if not row:
            current_app.logger.warning(f"Nenhum procedimento encontrado com ID: {id}")
            return jsonify({'error': 'Procedimento não encontrado.'}), 404

        # Excluir o procedimento
        cursor.execute("DELETE FROM Procedimento WHERE id = ?", (id,))
        conn.commit()
        current_app.logger.info(f"Procedimento com ID {id} excluído com sucesso.")

        return jsonify({'message': 'Procedimento excluído com sucesso!'}), 200
    except Exception as e:
        current_app.logger.error(f"Erro ao excluir procedimento: {e}")
        return jsonify({'error': 'Erro ao excluir procedimento.', 'details': str(e)}), 500
    finally:
        if 'conn' in locals():
            conn.close()