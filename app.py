from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from models import db, Artista, Dia, Escenario, Show, Sponsor

app = Flask(__name__, template_folder='templates')
port = 5000

# Configuración de SQLAlchemy y base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:postgres@localhost:5432/postgres'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
engine = create_engine("postgresql+psycopg2://postgres:postgres@localhost:5432/postgres")

# Ruta principal que renderiza index.html
@app.route('/')
def home():
    return render_template('index.html')

# Ruta para obtener artistas por día
@app.route('/dia/<int:id_dia>', methods=["GET"])
def obtener_artistas(id_dia):
    conn = engine.connect()
    try:
        # Consulta para obtener los artistas por id_dia
        query = text("SELECT s.id_dia, a.id_artista, a.nombre, d.fecha FROM artistas a, dias d, shows s WHERE s.id_artista = a.id_artista AND d.id_dia = :id_dia AND s.id_dia = d.id_dia")
        result = conn.execute(query, {'id_dia': id_dia})
        artistas = result.fetchall()
        
        lista_artistas = []
        for artista in artistas:
            artista_data = {
                'id_dia': artista.id_dia,
				'id': artista.id_artista,
                'nombre': artista.nombre,
                'fecha': artista.fecha
            }
            lista_artistas.append(artista_data)
        
        return jsonify(lista_artistas), 200
    
    except SQLAlchemyError as e:
        return jsonify({"mensaje": "Error al consultar la base de datos.", "error": str(e)}), 500

if __name__ == '__main__':
    print('Starting server...')
    db.init_app(app)
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', debug=True, port=port)
    print('Started...')
