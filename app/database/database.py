import pyodbc
import os
import pymssql



def get_connection():
    try:
        conn = pymssql.connect(
            server='DESKTOP-MVVV575,1433',
            database='Inst_Mari_Lelo',
            user='Victor',
            password='231136'
        )
        print("Conexão bem-sucedida com o banco de dados!")
        return conn
    except Exception as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        raise