from flask import Flask, render_template, request, session, redirect, url_for
from flask_mysqldb import MySQL
import MySQLdb, json

"""Configuración del framework Flask"""
app = Flask(__name__)
app.secret_key = "1234534534"

"""Informacion de acceso a la bbdd, en este caso para local cuando se sube a pythonanywhere hay que modificar esta parte con la informacion que nos pone en la pestaña databases"""
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = ""
app.config["MYSQL_DB"] = "clinica"

db = MySQL(app)

"""Método de entrada, nos lleva a la pantalla de conocenos con información de la clinica"""
@app.route('/', methods=['GET', 'POST'])
def inicio():
    cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT DISTINCT(especialidad) FROM medico")
    especialidades = cursor.fetchall()
    
    return render_template("inicio.html", data=especialidades)

"""Se controla todo el proceso de login para el usuario y carga del mismo login"""
@app.route('/login', methods=['GET', 'POST'])
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
        return render_template('login.html')
"""Proceso de login para los medicos"""
@app.route('/medico-login', methods=['GET', 'POST'])
def medico_login():

    if 'usuario' in request.form and 'password' in request.form:
        usuario = request.form['usuario']
        password = request.form['password']
        cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM medico WHERE usuario=LOWER(%s) AND password=%s",(usuario,password))
        info = cursor.fetchone()
        if info is not None:
            if info['usuario'] == usuario.lower() and info["password"] == password:
                session['medico'] = usuario
                return redirect(url_for('citas_medico'))
        else:
            return "No existe ningun medico con dicho usuario o contraseña"
    else:
        return "falta información para el acceso"


"""Al pulsar el botón de registro nos muestra la pagina de registro de usuario"""
@app.route('/register')
def register():
    return render_template('register.html')

"""Cuando damos a guardar este metodo comprueba que no haya un usuario con el mismo dni y si no lo hay lo guarda"""
@app.route('/new',methods=['POST'])
def new():
    dni = request.form['dni']
    password = request.form['password']
    nombre = request.form['nombre']
    apellidos = request.form['apellidos']
    localidad = request.form['localidad']
    email = request.form['email']
    telefono = request.form['telefono']
    
    cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM paciente WHERE dni=%s",(dni,))
            
    info = cursor.fetchone()
    if info is None:
        consulta = "insert into paciente (dni, nombre, apellidos, localidad, password, email, telefono) values (UPPER(%s), %s, %s, %s, %s, %s, %s)"
        cursor.execute(consulta,(dni,nombre,apellidos,localidad,password, email, telefono))
        db.connection.commit()
        return render_template('login.html')
    else:
        return "ya se encuentra registrado un usuario con dni: "+dni

"""Cuando hacemos log con el paciente nos cargara la pagina con las citas desde hoy en adelante y nos da la opción de cancelarla"""
@app.route('/citas')
def citas():
    if session['usuario'] is not None:
        dni = session['usuario']
        cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT CONCAT(medico.nombre, ' ', medico.apellidos) AS medico, cita.fecha, consulta.nombre AS consulta, CONCAT(paciente.nombre, ' ', paciente.apellidos) as paciente, cita.id as id, cita.hora as hora FROM cita JOIN medico ON cita.medico = medico.id JOIN consulta ON medico.consulta = consulta.id JOIN paciente ON cita.paciente=paciente.id WHERE paciente.dni=%s and cita.fecha >= CURDATE() ORDER BY cita.fecha ASC, cita.hora ASC",(dni,))
        info = cursor.fetchall()
        cursor.execute("SELECT CONCAT(paciente.nombre, ' ', paciente.apellidos) as paciente FROM paciente WHERE paciente.dni=%s",(dni,))
        nombre = cursor.fetchone()
        if len(info) > 0:
            return render_template('citas.html', data=info, usuario=nombre['paciente'])
        else:
            return render_template('citas.html', usuario=nombre['paciente'])
    else:
        return render_template('login.html')

"""Al pulsar en el botón de cerrar sesión hace logout"""
@app.route('/logout')
def logout():
    session.pop('usuario', None)
    session.pop('medico', None)
    return redirect(url_for('index'))


"""Al pulsar en el botón de nueva cita nos abre la ventana para solicitar la cita"""
@app.route('/nueva-cita')
def nueva_cita():
    cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM medico")
    primera = cursor.fetchall()
    cursor.execute("SELECT DISTINCT especialidad FROM medico")
    segunda =cursor.fetchall()

    return render_template("nueva-cita.html", medicos = primera, especialidades = segunda)

"""Cuando seleccionamos la cita y le damos a guardar se guarda en base de datos"""
@app.route("/guardar-cita", methods=['POST'])
def guardar_cita():
    
    medico = request.form['medico']
    fecha = request.form['fecha']
    hora = request.form['hora']
    cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT id FROM paciente WHERE dni=%s",(session['usuario'],))
    usuario = cursor.fetchone()
    
    cursor.execute("INSERT INTO cita (paciente, medico, fecha, hora) values (%s, %s, %s, %s)",(usuario['id'],medico,fecha,hora))
    db.connection.commit()
    return redirect(url_for('citas'))

"""Desde la tabla si pulsamos el boton de cancelar cita se elimina de base de datos"""
@app.route("/eliminar-cita", methods=['POST'])
def eliminar_cita():
    id = request.form['id']
    cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("DELETE FROM cita WHERE id=%s",(id,))
    db.connection.commit()

    return redirect(url_for('citas'))

"""cuando hacemos log con el medico nos muestra las citas del dia y la información del usuario"""
@app.route('/citas-medico')
def citas_medico():
    if session['medico'] is not None:
        usuario = session['medico']
        cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT CONCAT(paciente.nombre, ' ', paciente.apellidos) as paciente, cita.fecha as fecha, consulta.nombre as consulta, cita.hora as hora, paciente.email as email, paciente.telefono as telefono  from paciente join cita on cita.paciente = paciente.id join medico on cita.medico = medico.id join consulta on medico.consulta = consulta.id WHERE medico.usuario=%s AND cita.fecha = CURDATE() ORDER BY cita.fecha ASC, cita.hora ASC",(usuario,))
        info = cursor.fetchall()
        cursor.execute("SELECT CONCAT(medico.nombre, ' ', medico.apellidos) as medico FROM medico WHERE medico.usuario=%s",(usuario,))
        nombre = cursor.fetchone()
        if len(info) > 0:
            return render_template('citas-medico.html', data=info, usuario=nombre['medico'])
        else:
            return render_template('citas-medico.html', usuario=nombre['medico'])
    else:
        return render_template('login.html')

"""Metodo para ser llamado mediante ajax que nos devuele las horas disponibles del medico y del propio paciente, no puediendo repetirse"""
@app.route('/horas',methods=['POST'])
def horas():
    usuario = session["usuario"]
    medico = request.form['medico']
    fecha = request.form['fecha']

    cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT hora FROM cita WHERE cita.medico = %s AND cita.fecha = %s UNION SELECT hora FROM cita JOIN paciente ON cita.paciente = paciente.id WHERE paciente.dni = %s AND cita.fecha = %s",(medico, fecha, usuario, fecha))
    horas = cursor.fetchall()
    if len(horas) > 0:
        return json.dumps(horas)
    else:
        return "0"



if __name__ == '__main__':
    app.run(debug=True)