import logging
import os
from logging.handlers import RotatingFileHandler
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from werkzeug.exceptions import HTTPException

from flask import Flask, render_template, redirect, url_for, flash, request, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DecimalField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'clave-super-secreta-mini-videojuegos-2026'
# MODIFICACIÓN 1: Usamos memoria para las pruebas y no afectar tu MySQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Debes iniciar sesión para acceder.'

# ---------- CONFIGURACIÓN DE SENTRY Y LOGS ----------
SENTRY_DSN = os.environ.get("SENTRY_DSN", "")
if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[FlaskIntegration()],
        traces_sample_rate=0.0
    )

if not os.path.exists("logs"):
    os.makedirs("logs")
file_handler = RotatingFileHandler("logs/errors.log", maxBytes=5*1024*1024, backupCount=5, encoding="utf-8")
file_handler.setLevel(logging.ERROR)
file_handler.setFormatter(logging.Formatter("[%(asctime)s] %(levelname)s en %(module)s: %(message)s"))
app.logger.addHandler(file_handler)

# ---------- MODELOS ----------
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(120), unique=True, index=True)
    password_hash = db.Column(db.String(255))

    @property
    def password(self):
        raise AttributeError('password no es legible')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

class Juego(db.Model):
    __tablename__ = 'juegos'
    # MODIFICACIÓN 3: Cambiado BigInteger a Integer con autoincrement para que SQLite funcione
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(255), nullable=False)
    descripcion = db.Column(db.String(255), nullable=False)
    precio = db.Column(db.Numeric(9, 2), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ---------- FORMULARIOS ----------
class LoginForm(FlaskForm):
    username = StringField('Usuario', validators=[DataRequired()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    remember_me = BooleanField('Recordarme')
    submit = SubmitField('Ingresar')

class RegistrationForm(FlaskForm):
    username = StringField('Usuario', validators=[DataRequired(), Length(1, 64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired(), EqualTo('password2', message='Las contraseñas deben coincidir.')])
    password2 = PasswordField('Confirmar contraseña', validators=[DataRequired()])
    submit = SubmitField('Registrar')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Usuario ya en uso.')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email ya registrado.')

class JuegoForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired(), Length(1, 255)])
    descripcion = TextAreaField('Descripción', validators=[DataRequired(), Length(1, 255)])
    precio = DecimalField('Precio', validators=[DataRequired()])
    submit = SubmitField('Guardar')

# ---------- RUTAS ----------
@app.route('/')
def index():
    juegos = Juego.query.all()
    return render_template('index.html', juegos=juegos)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.password = form.password.data
        db.session.add(user)
        db.session.commit()
        flash('Ahora puedes iniciar sesión.')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        flash('Usuario o contraseña inválidos.')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Sesión cerrada.')
    return redirect(url_for('index'))

@app.route('/juego/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo_juego():
    form = JuegoForm()
    if form.validate_on_submit():
        juego = Juego(nombre=form.nombre.data, descripcion=form.descripcion.data, precio=form.precio.data)
        db.session.add(juego)
        db.session.commit()
        flash('Juego agregado.')
        return redirect(url_for('index'))
    return render_template('juego_form.html', form=form, titulo='Nuevo Juego')

@app.route('/juego/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_juego(id):
    juego = Juego.query.get_or_404(id)
    form = JuegoForm(obj=juego)
    if form.validate_on_submit():
        juego.nombre = form.nombre.data
        juego.descripcion = form.descripcion.data
        juego.precio = form.precio.data
        db.session.commit()
        flash('Juego actualizado.')
        return redirect(url_for('index'))
    return render_template('juego_form.html', form=form, titulo='Editar Juego')

@app.route('/juego/eliminar/<int:id>', methods=['POST'])
@login_required
def eliminar_juego(id):
    juego = Juego.query.get_or_404(id)
    db.session.delete(juego)
    db.session.commit()
    flash('Juego eliminado.')
    return redirect(url_for('index'))

# =========================================================
#  RUTAS DE PRUEBA PARA LA ACTIVIDAD (U1 - A5)
# =========================================================
@app.route('/juego/buscar/<int:id>')
def buscar_juego(id):
    if id <= 0:
        abort(400, description="El ID debe ser un entero positivo.") # Dispara 400
    juego = Juego.query.get(id)
    if juego is None:
        abort(404, description="Juego no encontrado") # Dispara 404
    return f"Juego encontrado: {juego.nombre}"

@app.route('/boom')
def boom():
    return 1 / 0  # Dispara 500 y se guarda en errors.log

@app.route('/api/prueba')
def api_prueba():
    abort(404, description="Ruta de API no encontrada") # Dispara JSON 404

# =========================================================
#  MANEJADORES DE ERRORES
# =========================================================
@app.errorhandler(HTTPException)
def handle_http_exception(e):
    if request.path.startswith("/api/"):
        response = e.get_response()
        response.data = jsonify({
            "code": e.code,
            "name": e.name,
            "description": e.description,
        }).get_data()
        response.content_type = "application/json"
        return response
    return render_template("500.html", error=e), e.code or 500

@app.errorhandler(400)
def bad_request(e):
    app.logger.warning(f"400 Bad Request en {request.path}: {e}")
    return render_template("400.html", error=e), 400

@app.errorhandler(404)
def not_found(e):
    return render_template("404.html", error=e), 404

@app.errorhandler(405)
def method_not_allowed(e):
    return render_template("405.html", error=e), 405

@app.errorhandler(500)
def internal_error(e):
    original = getattr(e, "original_exception", e)
    app.logger.error(f"500 Internal Server Error en {request.path}: {original}", exc_info=True)
    return render_template("500.html", error=e), 500

@app.errorhandler(Exception)
def handle_unexpected_error(e):
    if isinstance(e, HTTPException):
        return e
    app.logger.exception(f"Excepción no controlada en {request.path}: {e}")
    return render_template("500.html", error=e), 500

# MODIFICACIÓN 2: Agregamos la función create_app para las pruebas
def create_app(config_name='testing'):
    return app

if __name__ == '__main__':
    app.run(debug=False)