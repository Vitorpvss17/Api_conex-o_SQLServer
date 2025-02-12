from app import create_app
from waitress import serve

app = create_app()


        

if __name__ == '__main__':
    serve(
        app,
        host="0.0.0.0",
        port=5000,
        threads=4,  # Número de threads para lidar com requisições
        url_prefix="/api",  # Prefixo de URL (opcional)
    )