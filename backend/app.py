from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from models import db, Artista, Dia, Escenario, Show, Sponsor

app = Flask(__name__)
port = 5000
#le pasas a sqlalchemy la url de la base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:ACN041003@localhost:5432/postgres'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
engine = create_engine("postgresql+psycopg2://postgres:ACN041003@localhost:5432/postgres")

@app.route('/')
def home():
  dias = Dia.query.all()
  return render_template('index.html', dias=dias)

app = Flask(__name__)

@app.route('/<id_dia>/')
def obtener_artistas():
	conn = engine.connect()
	try:
		# Consulta para obtener los artistas por id_dia
		query = text("Select a.nombre, a.imagen, d.fecha from artistas a, dias d, shows s where s.id_artista = a.id_artista and d.id_dia = id_dia and s.id_dia = d.id_dia;")
		result = conn.execute(query)
		artistas = result.fetchall()
		lista_artistas = []
		for artista in artistas:
			artista_data = {
				'id': artista.id_artista,
				'nombre': artista.nombre,
				'imagen': artista.imagen,  # nos falta
				'fecha': artista.fecha
			}
			lista_artistas.append(artista_data)
		return jsonify(lista_artistas), 200
	except:
		return jsonify({"mensaje": "No hay artistas."}), 500

if __name__ == '__main__':
	print('Starting server...')
	db.init_app(app)
	with app.app_context():
		db.create_all()
	app.run(host='0.0.0.0', debug=True, port=port)
	print('Started...')