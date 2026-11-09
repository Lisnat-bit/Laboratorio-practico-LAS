import sqlite3
import re
from datetime import datetime
from flask import Flask, render_template, request
# Criterio 6: Módulo para protección de contraseñas mediante Hash
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# Asegurar que la tabla exista al iniciar con la estructura correcta
def crear_tabla():
    conexion = sqlite3.connect('usuarios.db')
    cursor = conexion.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT NOT NULL,
            correo TEXT NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conexion.commit()
    conexion.close()

# Criterio 7: Función obligatoria para registrar eventos en eventos.log
def registrar_evento(tipo, usuario):
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("eventos.log", "a", encoding="utf-8") as archivo:
        archivo.write(f"{fecha},{tipo},{usuario}\n")

@app.route("/")
def inicio():
    return "Laboratorio de Ciberseguridad"

# --- FUNCIONES DE VALIDACIÓN (Criterio 4 y 5) ---
def validar_usuario(usuario):
    return re.fullmatch(r"[A-Za-z0-9_]{4,20}", usuario) is not None

def validar_correo(correo):
    return re.fullmatch(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$", correo) is not None

def validar_password(password):
    return len(password) >= 8

# --- RUTA DE REGISTRO ---
@app.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        # Saneamiento y Normalización (Paso 3)
        usuario = request.form.get("usuario", "").strip()
        correo = request.form.get("correo", "").strip()
        password = request.form.get("password", "")

        # Validaciones de Entrada
        if not validar_usuario(usuario):
            return "Usuario inválido"
        if not validar_correo(correo):
            return "Correo electrónico inválido"
        if not validar_password(password):
            return "La contraseña debe contener al menos 8 caracteres"

        # Criterio 5: Verificar usuarios o correos duplicados (Paso 8)
        conexion = sqlite3.connect('usuarios.db')
        cursor = conexion.cursor()
        cursor.execute("SELECT id FROM usuarios WHERE usuario = ? OR correo = ?", (usuario, correo))
        existente = cursor.fetchone()
        
        if existente:
            conexion.close()
            return "El usuario o correo ya está registrado"

        # Criterio 6: Almacenamiento seguro usando Hash en lugar de texto plano
        password_hash = generate_password_hash(password)
        
        # Consultas Parametrizadas para evitar Inyección SQL
        cursor.execute(
            "INSERT INTO usuarios (usuario, correo, password) VALUES (?, ?, ?)",
            (usuario, correo, password_hash)
        )
        conexion.commit()
        conexion.close()

        return "Usuario registrado"
        
    return render_template("registro.html")

# --- RUTA DE LOGIN ---
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form.get("usuario", "").strip()
        password = request.form.get("password", "")

        conexion = sqlite3.connect('usuarios.db')
        cursor = conexion.cursor()
        # Consulta parametrizada buscando solo por el nombre de usuario
        cursor.execute("SELECT * FROM usuarios WHERE usuario = ?", (usuario,))
        resultado = cursor.fetchone()
        conexion.close()

        # Criterio 6: Validación segura descifrando el hash con check_password_hash
        if resultado and check_password_hash(resultado[3], password):
            registrar_evento("LOGIN_CORRECTO", usuario)
            return "Inicio de sesión correcto"
        else:
            registrar_evento("LOGIN_FALLIDO", usuario)
            return "Credenciales incorrectas"
            
    return render_template("login.html")

if __name__ == "__main__":
    crear_tabla()
    app.run(debug=True)