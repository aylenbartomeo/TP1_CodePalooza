from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Artista(db.Model):
  __tablename__ = 'artistas'
  id_artista = db.Column(db.Integer, primary_key=True)
  nombre = db.Column(db.String(255), nullable=False)
  es_banda = db.Column(db.Boolean, nullable=False)
  nacionalidad = db.Column(db.String(255), nullable=False)
  genero = db.Column(db.String(255), nullable=False)

class Dia(db.Model):
  __tablename__ = 'dias'
  id_dia = db.Column(db.Integer, primary_key=True)
  fecha = db.Column(db.Date, nullable=False)

class Escenario(db.Model):
  __tablename__ = 'escenario'
  id_escenario = db.Column(db.Integer, primary_key=True)
  nombre = db.Column(db.String(255), nullable=False)

class Show(db.Model):
  __tablename__ = 'shows'
  # foreign key de id en 'dias'
  id_dia = db.Column(db.Integer, db.ForeignKey('dias.id'), nullable=False)
  # foreign key de id en 'artistas'
  id_artista = db.Column(db.Integer, db.ForeignKey('artistas.id'), nullable=False)
  # foreign key de id en 'escenario'
  id_escenario = db.Column(db.Integer, db.ForeignKey('escenario.id'), nullable=False)
  duracion = db.Column(db.Integer, nullable=False)

class Sponsor(db.Model):
  __tablename__ = 'sponsors'
  id_sponsors = db.Column(db.Integer, primary_key=True)
  nombre = db.Column(db.String(255), nullable=False)
  # foreign key de id en 'dias'
  id_dia = db.Column(db.Integer, db.ForeignKey('dias.id'), nullable=False)