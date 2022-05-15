from flask import Flask, render_template, request, session, redirect, url_for
from flask_mysqldb import MySQL
import MySQLdb, json

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
                if info['dni'] == dni.upper() and info["password"] == password:
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
        cursor.execute("SELECT CONCAT(medico.nombre, ' ', medico.apellidos) AS medico, cita.fecha, consulta.nombre AS consulta, CONCAT(paciente.nombre, ' ', paciente.apellidos) as paciente, cita.id as id FROM cita JOIN medico ON cita.medico = medico.id JOIN consulta ON medico.consulta = consulta.id JOIN paciente ON cita.paciente=paciente.id WHERE paciente.dni=%s",(dni,))
        info = cursor.fetchall()
        cursor.execute("SELECT CONCAT(paciente.nombre, ' ', paciente.apellidos) as paciente FROM paciente WHERE paciente.dni=%s",(dni,))
        nombre = cursor.fetchone()
        if len(info) > 0:
            return render_template('citas.html', data=info, usuario=nombre['paciente'])
        else:
            return render_template('citas.html', usuario=nombre['paciente'])
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

@app.route('/nueva-cita')
def nueva_cita():
    cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM medico")
    primera = cursor.fetchall()
    cursor.execute("SELECT DISTINCT especialidad FROM medico")
    segunda =cursor.fetchall()

    return render_template("nueva-cita.html", medicos = primera, especialidades = segunda)

@app.route("/guardar-cita", methods=['POST'])
def guardar_cita():
    
    medico = request.form['medico']
    fecha = request.form['fecha']
    cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT id FROM paciente WHERE dni=%s",(session['usuario'],))
    usuario = cursor.fetchone()
    
    cursor.execute("INSERT INTO cita (paciente, medico, fecha) values (%s, %s, %s)",(usuario['id'],medico,fecha))
    db.connection.commit()
    return redirect(url_for('citas'))

@app.route("/eliminar-cita", methods=['POST'])
def eliminar_cita():
    id = request.form['id']
    cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("DELETE FROM cita WHERE id=%s",(id,))
    db.connection.commit()

    return redirect(url_for('citas'))

if __name__ == '__main__':
    app.run(debug=True)