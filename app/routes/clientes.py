from flask import Blueprint, request, jsonify, current_app, send_from_directory
from app.database.database import get_connection
import os
import base64
import time
import imghdr
from werkzeug.utils import secure_filename

# Inicialização do blueprint
clientes_bp = Blueprint('clientes', __name__)

# Configuração do diretório para salvar imagens
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'imagens_clientes')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Função para listar clientes
@clientes_bp.route('/', methods=['GET'])
def listar_clientes():
    try:
        current_app.logger.info("Tentando conectar ao banco de dados...")
        conn = get_connection()
        cursor = conn.cursor()
        current_app.logger.info("Conexão estabelecida, executando consulta SQL...")

        cursor.execute("SELECT id, nome, sobrenome, email, telefone, foto FROM Clientes")
        rows = cursor.fetchall()
        current_app.logger.info(f"Linhas retornadas: {len(rows)}")

        clientes = [
            {'id': row[0], 'nome': row[1], 'sobrenome': row[2], 'email': row[3], 'telefone': row[4], 'foto': row[5]}
            for row in rows
        ]
        return jsonify(clientes), 200
    except Exception as e:
        current_app.logger.error(f"Erro ocorrido ao listar clientes: {e}")
        return jsonify({'error': 'Erro ao listar clientes.', 'details': str(e)}), 500
    finally:
        if 'conn' in locals():
            conn.close()

# Função para criar um cliente
@clientes_bp.route('/', methods=['POST'])
def criar_cliente():
    try:
        data = request.json
        current_app.logger.info(f"Dados recebidos para criação de cliente: {data}")

        # Validação de campos obrigatórios
        nome = data.get('nome')
        sobrenome = data.get('sobrenome')
        email = data.get('email')
        telefone = data.get('telefone')
        foto = data.get('foto')

        if not all([nome, sobrenome, email, telefone]):
            current_app.logger.warning("Campos obrigatórios ausentes na solicitação.")
            return jsonify({'error': 'Todos os campos obrigatórios devem ser preenchidos.'}), 400

        # Processar a imagem, se fornecida
        if foto:
            image_data = base64.b64decode(foto)
            image_type = imghdr.what(None, h=image_data)

            if not image_type:
                current_app.logger.warning("Arquivo de imagem inválido.")
                return jsonify({'error': 'Arquivo de imagem inválido.'}), 400

            image_name = f"{secure_filename(nome)}_{secure_filename(sobrenome)}_{int(time.time())}.png"
            image_path = os.path.join(UPLOAD_FOLDER, image_name).replace("\\", "/")

            with open(image_path, 'wb') as img_file:
                img_file.write(image_data)

            foto_caminho = image_name  # Caminho da imagem a ser armazenado no banco
        else:
            foto_caminho = None

        # Inserir dados no banco de dados
        current_app.logger.info("Tentando conectar ao banco de dados...")
        conn = get_connection()
        cursor = conn.cursor()
        current_app.logger.info("Conexão estabelecida, executando consulta SQL...")

        cursor.execute(
            """
            INSERT INTO Clientes (nome, sobrenome, email, telefone, foto)
            VALUES (?, ?, ?, ?, ?)
            """,
            (nome, sobrenome, email, telefone, foto_caminho)
        )
        conn.commit()
        current_app.logger.info("Cliente criado com sucesso no banco de dados.")

        return jsonify({'message': 'Cliente criado com sucesso!'}), 201
    except Exception as e:
        current_app.logger.error(f"Erro ao criar cliente: {e}")
        return jsonify({'error': 'Erro ao criar cliente.', 'details': str(e)}), 500
    finally:
        if 'conn' in locals():
            conn.close()

# Função para excluir cliente
@clientes_bp.route('/<int:id>', methods=['DELETE'])
def excluir_cliente(id):
    try:
        current_app.logger.info(f"Tentando excluir cliente com ID: {id}")
        conn = get_connection()
        cursor = conn.cursor()

        # Buscar o caminho da imagem antes de excluir o cliente
        cursor.execute("SELECT foto FROM Clientes WHERE id = ?", (id,))
        row = cursor.fetchone()

        if not row:
            current_app.logger.warning(f"Nenhum cliente encontrado com ID: {id}")
            return jsonify({'error': 'Cliente não encontrado.'}), 404

        foto_caminho = row[0]
        
        # Excluir o cliente do banco
        cursor.execute("DELETE FROM Clientes WHERE id = ?", (id,))
        conn.commit()

        if foto_caminho and os.path.exists(os.path.join(UPLOAD_FOLDER, foto_caminho)):
            os.remove(os.path.join(UPLOAD_FOLDER, foto_caminho))
            current_app.logger.info(f"Imagem {foto_caminho} excluída com sucesso.")

        current_app.logger.info(f"Cliente com ID {id} excluído com sucesso.")
        return jsonify({'message': 'Cliente excluído com sucesso!'}), 200
    except Exception as e:
        current_app.logger.error(f"Erro ao excluir cliente: {e}")
        return jsonify({'error': 'Erro ao excluir cliente.', 'details': str(e)}), 500
    finally:
        if 'conn' in locals():
            conn.close()

# Função para servir imagens
@clientes_bp.route('/imagens/<path:filename>', methods=['GET'])
def servir_imagens(filename):
    try:
        return send_from_directory(UPLOAD_FOLDER, filename)
    except Exception as e:
        current_app.logger.error(f"Erro ao servir imagem: {e}")
        return jsonify({'error': 'Erro ao carregar imagem.', 'details': str(e)}), 500