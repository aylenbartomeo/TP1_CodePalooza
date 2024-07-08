import base64
from flask import Flask, request, jsonify, render_template, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker
from models import db, Artista, Dia, Escenario, Show, Sponsor

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

# Ruta para ir al formulario
@app.route('/form')
def formulario():
    return render_template('formulario.html')

# Ruta para ir a la seccion de sponsors
@app.route('/sponsors')
def sponsors():
    conn = engine.connect()
    try:
        # Consulta para obtener todos los sponsors
        query = text("SELECT id_sponsors, nombre, id_dia FROM sponsors")
        result = conn.execute(query)
        sponsors = result.fetchall()

        return render_template('sponsors.html', sponsors=sponsors)

    except SQLAlchemyError as e:
        return jsonify({"mensaje": "Error al consultar la base de datos.", "error": str(e)}), 500

    finally:
        conn.close()

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
                'imagen': base64.b64encode(artista.fotos).decode('utf-8') if artista.fotos else None,
                'fecha': artista.fecha
            }
            lista_artistas.append(artista_data)
        return render_template('artistas.html', artistas=lista_artistas, id_dia=id_dia), 200
    
    except SQLAlchemyError as e:
        return jsonify({"mensaje": "Error al consultar la base de datos.", "error": str(e)}), 500

# Ruta para ver la informacion de cada artista
@app.route('/artista/<int:id_artista>/')
def ver_artista(id_artista):
    conn = engine.connect()
    try:
        # Consulta para obtener los detalles del artista por id_artista
        query = text("SELECT a.id_artista, a.nombre, a.es_banda, a.nacionalidad, a.genero, a.fotos, e.nombre as nombre_escenario FROM artistas a "
                     "JOIN shows s ON s.id_artista = a.id_artista "
                     "JOIN escenario e ON s.id_escenario = e.id_escenario "
                     "WHERE a.id_artista = :id_artista")
        result = conn.execute(query, {'id_artista': id_artista})
        artista = result.fetchone()

        if not artista:
            return jsonify({"mensaje": "Artista no encontrado"}), 404

        # Convertir la imagen a base64 para mostrar en cartas.html
        imagen_base64 = base64.b64encode(artista.fotos).decode('utf-8') if artista.fotos else None

        return render_template('cartas.html', artista={
            'id': id_artista,
            'nombre': artista.nombre,
            'es_banda': artista.es_banda,
            'nacionalidad': artista.nacionalidad,
            'genero': artista.genero,
            'imagen': imagen_base64,
            'nombre_escenario': artista.nombre_escenario
        }), 200

    except SQLAlchemyError as e:
        return jsonify({"mensaje": "Error al consultar la base de datos.", "error": str(e)}), 500
    finally:
        conn.close()

# Ruta para eliminar un artista por ID
@app.route('/artista/<int:id_artista>/', methods=["DELETE"])
def remover_artista(id_artista):
    conn = engine.connect()
    try:
        # Eliminar shows relacionados
        delete_shows_query = text("DELETE FROM shows WHERE id_artista = :id_artista")
        conn.execute(delete_shows_query, {'id_artista': id_artista})

        # Eliminar el artista
        delete_artista_query = text("DELETE FROM artistas WHERE id_artista = :id_artista")
        conn.execute(delete_artista_query, {'id_artista': id_artista})

        # Commit de la transacción
        conn.commit()

        # Redireccionar a la página anterior
        return redirect(request.referrer)

    except SQLAlchemyError as e:
        conn.rollback()
        error_message = f"Error al eliminar el artista con ID {id_artista}: {str(e)}"
        print(error_message)  # Imprimir el error en la consola para depuración
        return jsonify({"mensaje": "Error al eliminar el artista.", "error": str(e)}), 500
    
    finally:
        conn.close()

# Endpoint para agregar un nuevo artista
@app.route('/agregar_artista', methods=['POST'])
def agregar_artista():
    data = request.form
    nombre = data.get('nombre')
    genero = data.get('genero')
    nacionalidad = data.get('nacionalidad')
    es_banda = data.get('es_banda') == 'Banda'
    id_dia = data.get('dia')
    id_escenario = data.get('escenario')
    duracion = data.get('duracion')

    imagen = request.files.get('imagen')
    imagen_data = imagen.read() if imagen else None

    session = Session()
    try:
        nuevo_artista = Artista(
            nombre=nombre,
            genero=genero,
            nacionalidad=nacionalidad,
            es_banda=es_banda,
            fotos=imagen_data
        )
        session.add(nuevo_artista)
        session.flush()

        nuevo_show = Show(
            id_dia=id_dia,
            id_artista=nuevo_artista.id_artista,
            id_escenario=id_escenario,
            duracion=duracion
        )
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
