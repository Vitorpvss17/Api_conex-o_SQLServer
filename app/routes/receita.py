from flask import Blueprint, request, jsonify, current_app
from app.database.database import get_connection

# Inicialização do blueprint
receita_bp = Blueprint('receita', __name__)

@receita_bp.route('/', methods=['GET'])
def listar_receitas():
    cliente_id = request.args.get('clienteId')
    try:
        current_app.logger.info(f"Tentando listar receitas para o cliente ID: {cliente_id}")
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT id, clienteId, data, servico, titulo, descricao, valor FROM Receitas WHERE clienteId = ?", (cliente_id,))
        rows = cursor.fetchall()

        receitas = [
            {
                'id': row[0],
                'clienteId': row[1],
                'data': row[2].strftime('%Y-%m-%d'),  # Formatar data
                'servico': row[3],
                'titulo': row[4],  # Incluindo o campo titulo
                'descricao': row[5],  # Incluindo o campo descricao
                'valor': float(row[6])  # Incluindo o campo valor
            }
            for row in rows
        ]

        current_app.logger.info(f"Receitas encontradas: {len(receitas)}")
        return jsonify(receitas), 200
    except Exception as e:
        current_app.logger.error(f"Erro ao listar receitas: {e}")
        return jsonify({'error': 'Erro ao listar receitas.', 'details': str(e)}), 500
    finally:
        if 'conn' in locals():
            conn.close()

@receita_bp.route('/', methods=['POST'])
def criar_receita():
    try:
        data = request.json
        current_app.logger.info(f"Dados recebidos para criação de receita: {data}")

        # Validação de campos obrigatórios
        cliente_id = data.get('clienteId')
        data_receita = data.get('data')
        servico = data.get('servico')
        titulo = data.get('titulo')  # Novo campo
        descricao = data.get('descricao')  # Novo campo
        valor = data.get('valor')  # Novo campo

        if not all([cliente_id, data_receita, servico, titulo, descricao, valor]):
            current_app.logger.warning("Campos obrigatórios ausentes na solicitação.")
            return jsonify({'error': 'Todos os campos obrigatórios devem ser preenchidos.'}), 400

        # Inserir dados no banco de dados
        current_app.logger.info("Tentando conectar ao banco de dados...")
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO Receitas (clienteId, data, servico, titulo, descricao, valor)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (cliente_id, data_receita, servico, titulo, descricao, valor)  # Incluindo os novos campos
        )
        conn.commit()
        current_app.logger.info("Receita criada com sucesso no banco de dados.")

        return jsonify({'message': 'Receita criada com sucesso!'}), 201
    except Exception as e:
        current_app.logger.error(f"Erro ao criar receita: {e}")
        return jsonify({'error': 'Erro ao criar receita.', 'details': str(e)}), 500
    finally:
        if 'conn' in locals():
            conn.close()

@receita_bp.route('/<int:id>', methods=['DELETE'])
def excluir_receita(id):
    try:
        current_app.logger.info(f"Tentando excluir receita com ID: {id}")
        conn = get_connection()
        cursor = conn.cursor()

        # Verificar se a receita existe
        cursor.execute("SELECT id FROM Receitas WHERE id = ?", (id,))
        row = cursor.fetchone()

        if not row:
            current_app.logger.warning(f"Nenhuma receita encontrada com ID: {id}")
            return jsonify({'error': 'Receita não encontrada.'}), 404

        # Excluir a receita
        cursor.execute("DELETE FROM Receitas WHERE id = ?", (id,))
        conn.commit()
        current_app.logger.info(f"Receita com ID {id} excluída com sucesso.")

        return jsonify({'message': 'Receita excluída com sucesso!'}), 200
    except Exception as e:
        current_app.logger.error(f"Erro ao excluir receita: {e}")
        return jsonify({'error': 'Erro ao excluir receita.', 'details': str(e)}), 500
    finally:
        if 'conn' in locals():
            conn.close()