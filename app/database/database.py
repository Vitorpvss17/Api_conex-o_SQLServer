import pyodbc
import os
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

def get_connection():
    try:
        connection_string = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={{DESKTOP-MVVV575,1433}};"
            f"DATABASE={{Inst_Mari_Lelo}};"
            f"Trusted_Connection=yes;"  # Usando autenticação integrada do Windows
        )
        conn = pyodbc.connect(connection_string)
        print("Conexão bem-sucedida com o banco de dados!")
        return conn
    except Exception as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        raise