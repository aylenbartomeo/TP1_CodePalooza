import base64
from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from models import db, Artista, Dia, Escenario, Show, Sponsor
from sqlalchemy.orm import sessionmaker


app = Flask(__name__, template_folder='templates')
port = 5000

# Configuración de SQLAlchemy y base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:postgres@localhost:5432/postgres'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
engine = create_engine("postgresql+psycopg2://postgres:postgres@localhost:5432/postgres")
Session = sessionmaker(bind=engine)

# Ruta principal que renderiza index.html
@app.route('/')
def home():
    return render_template('index.html')


# Ruta para obtener artistas por día
@app.route('/dia/<int:id_dia>/', methods=["GET"])
def obtener_artistas(id_dia):
    conn = engine.connect()
    try:
        # Consulta para obtener los artistas por id_dia
        query = text("SELECT s.id_dia, a.id_artista, a.fotos, a.nombre, d.fecha FROM artistas a, dias d, shows s WHERE s.id_artista = a.id_artista AND d.id_dia = :id_dia AND s.id_dia = d.id_dia")
        result = conn.execute(query, {'id_dia': id_dia})
        artistas = result.fetchall()
        
        lista_artistas = []
        for artista in artistas:
            artista_data = {
                'id_dia': artista.id_dia,
				'id': artista.id_artista,
                'nombre': artista.nombre,
                # base64.b64encode es una función de Python que toma datos binarios (como los de una imagen) y los convierte en una cadena de texto base64.
                # .decode('utf-8') convierte esos bytes en una cadena de texto Unicode, que es lo que necesitamos para incrustarla en un src de imagen en HTML.
                # if artista.fotos else None comprueba si artista.fotos es None (es decir, si no hay imagen en la base de datos). En tal caso, asigna None a imagen.
                'imagen': base64.b64encode(artista.fotos).decode('utf-8') if artista.fotos else None,
                'fecha': artista.fecha
            }
            lista_artistas.append(artista_data)
        # Pasar la lista de artistas a la plantilla
        return render_template('artistas.html', artistas=lista_artistas, id_dia=id_dia), 200
    
    except SQLAlchemyError as e:
        return jsonify({"mensaje": "Error al consultar la base de datos.", "error": str(e)}), 500

# Ruta para ver la informacion de cada artista
@app.route('/artista/<int:id_artista>/')
def ver_artista(id_artista):
    conn = engine.connect()
    try:
        # Consulta para obtener los detalles del artista por id_artista
        query = text("SELECT id_artista, nombre, es_banda, nacionalidad, genero, fotos FROM artistas WHERE id_artista = :id_artista")
        result = conn.execute(query, {'id_artista': id_artista})
        artista = result.fetchone()

        if not artista:
            return jsonify({"mensaje": "Artista no encontrado"}), 404

        # Convertir la imagen a base64 para mostrar en cartas.html
        imagen_base64 = base64.b64encode(artista.fotos).decode('utf-8') if artista.fotos else None

        # Renderizar acartas.html con los datos del artista seleccionado
        return render_template('cartas.html', artista={
            'nombre': artista.nombre,
            'es_banda': artista.es_banda,
            'nacionalidad': artista.nacionalidad,
            'genero': artista.genero,
            'imagen': imagen_base64
        }), 200

    except SQLAlchemyError as e:
        return jsonify({"mensaje": "Error al consultar la base de datos.", "error": str(e)}), 500
    finally:
        conn.close()

# Ruta para ir al formulario
@app.route('/form')
def formulario():
    return render_template('formulario.html')

# Endpoint para agregar un nuevo artista
@app.route('/agregar_artista', methods=['POST'])
def agregar_artista():
    data = request.json
    nombre = data.get('nombre')
    genero = data.get('genero')
    nacionalidad = data.get('nacionalidad')
    es_banda = data.get('es_banda', False)  # Booleano
    id_dia = data.get('dia')
    id_escenario = data.get('escenario')

    session = Session()
    
    try:
        # Crear el artista
        nuevo_artista = Artista(nombre=nombre, genero=genero, nacionalidad=nacionalidad, es_banda=es_banda)
        session.add(nuevo_artista)
        session.commit()

        # Crear el show asociado al artista, día y escenario
        nuevo_show = Show(id_dia=id_dia, id_artista=nuevo_artista.id_artista, id_escenario=id_escenario)
        session.add(nuevo_show)
        session.commit()

        return jsonify({"mensaje": "Artista agregado exitosamente"}), 201

    except SQLAlchemyError as e:
        session.rollback()
        return jsonify({"mensaje": "Error al agregar el artista.", "error": str(e)}), 500

    finally:
        session.close()

if __name__ == '__main__':
    print('Starting server...')
    db.init_app(app)
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', debug=True, port=port)
    print('Started...')
