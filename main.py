from crypt import methods
from threading import local
from flask import Flask, render_template, request, session, redirect, url_for
from flask_mysqldb import MySQL
import MySQLdb

app = Flask(__name__)
app.secret_key = "1234534534"

app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = ""
app.config["MYSQL_DB"] = "clinica"

db = MySQL(app)

@app.route('/', methods=['GET', 'POST'])
def index():

    if request.method == 'POST':
        if 'dni' in request.form and 'password' in request.form:
            dni = request.form['dni']
            password = request.form['password']
            cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("SELECT * FROM paciente WHERE dni=UPPER(%s) AND password=%s",(dni,password))
            info = cursor.fetchone()
            if info is not None:
                if info['dni'] == dni and info["password"] == password:
                    session['usuario'] = dni
                    return redirect(url_for('citas'))
            else:
                return "fallo con el acceso, porfavor registrese primero"
        else:
            return "falta información para el acceso"
    else:
        return render_template('index.html')


@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/citas')
def citas():
    if session['usuario'] is not None:
        dni = session['usuario']
        cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT CONCAT(medico.nombre, ' ', medico.apellidos) AS medico, cita.fecha, consulta.nombre AS consulta, CONCAT(paciente.nombre, ' ', paciente.apellidos) as paciente FROM cita JOIN medico ON cita.medico = medico.id JOIN consulta ON medico.consulta = consulta.id JOIN paciente ON cita.paciente=paciente.id WHERE paciente.dni=%s",(dni,))
        info = cursor.fetchall()
        return render_template('citas.html', data=info)
    else:
        return render_template('index.html')

@app.route('/logout')
def logout():
    session.pop('usuario', None)
    return redirect(url_for('index'))

@app.route('/new',methods=['POST'])
def new():
    dni = request.form['dni']
    password = request.form['password']
    nombre = request.form['nombre']
    apellidos = request.form['apellidos']
    localidad = request.form['localidad']
    
    cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM paciente WHERE dni=%s",(dni,))
            
    info = cursor.fetchone()
    if info is None:
        consulta = "insert into paciente (dni, nombre, apellidos, localidad, password) values (UPPER(%s), %s, %s, %s, %s)"
        cursor.execute(consulta,(dni,nombre,apellidos,localidad,password))
        db.connection.commit()
        return render_template('index.html')
    else:
        return "ya se encuentra registrado un usuario con dni: "+dni

@app.route('/crear-cita')
def crear_cita():
    cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM medico")
    info = cursor.fetchall()

    return render_template("crear-cita.html", data=info)

if __name__ == '__main__':
    app.run(debug=True)