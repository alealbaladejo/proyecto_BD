import sys
import MySQLdb

def Conectar_BD(host, usuario, password, nombrebd):
    try:
        db = MySQLdb.connect(host, usuario, password, nombrebd)
        return db
    except MySQLdb.Error as e:
        print("No puedo conectar a la base de datos:", e)
        sys.exit(1)

def Desconectar_BD(db):
    db.close()

def Listar_Asignaturas(db):
    cursor = db.cursor(MySQLdb.cursors.DictCursor)
    sql = '''
    SELECT Nombre AS ASIGNATURA, COUNT(AA.ID_ASIGNATURA) AS ALUMNOS
    FROM ASIGNATURA_ALUMNO AA, ASIGNATURA A
    WHERE AA.ID_ASIGNATURA = A.ID_ASIGNATURA
    GROUP BY AA.ID_ASIGNATURA, ASIGNATURA    
    '''
    try:
        cursor.execute(sql)
        registros = cursor.fetchall()
        print("{:<20} {:<10}".format("ASIGNATURA", "ALUMNOS"))
        print("-" * 30)
        for registro in registros:
            print("{:<25} {:<10}".format(registro["ASIGNATURA"], registro["ALUMNOS"]))
    except MySQLdb.Error as e:
        print("Error en la consulta:", e)


def Sueldo_Profes(db):
    sueldominimo = float(input("Ingresa el sueldo más pequeño: "))
    sueldomaximo = float(input("Ingresa el sueldo más grande: "))
    sql = '''
    SELECT Nombre
    FROM PROFESOR
    WHERE sueldo BETWEEN %s AND %s''' % (sueldominimo,sueldomaximo)
    cursor = db.cursor()

    try:
        cursor.execute(sql)
        registros = cursor.fetchall()
        print ("Nombre Profesor")
        print("-"*30)
        for registro in registros:
            print(registro[0])
    except MySQLdb.Error as e:
        print("Error en la consulta:", e)
    if cursor.rowcount == 0:
        print("\nNo hay profesores entre esos sueldos")

def Alumnos_Asignatura(db):
    asig=input("Introduce una asignatura: ")
    sql='''
    SELECT A.Nombre AS ALUMNO
    FROM ALUMNO A, ASIGNATURA_ALUMNO AA, ASIGNATURA ASIG
    WHERE A.Num_Expediente = AA.Num_Expediente AND ASIG.ID_ASIGNATURA = AA.ID_ASIGNATURA
    AND Nota >= 5 AND ASIG.Nombre = %s
    '''

    cursor=db.cursor()
    
    try:
        cursor.execute(sql, (asig,))
        registros=cursor.fetchall()

        if len(registros)==0:
            print("No hay datos para mostrar.")
        if len(registros) > 0:
            print("Alumnos Aprobados")
            print("-"*30)
            for registro in registros:
                print (registro[0])
    except Exception as e:
        print("Error en la consulta", e)    


def Nuevo_Alumno(db, ALUMNO):
    cursor = db.cursor()
    sql = "INSERT INTO ALUMNO VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
    values = (
        ALUMNO["Num_Expediente"],
        ALUMNO["DNI"],
        ALUMNO["Nombre"],
        ALUMNO["Apellido_Paterno"],
        ALUMNO["Apellido_Materno"],
        ALUMNO["Direccion"],
        ALUMNO["ID_Grupo"],
        ALUMNO["Correo_Electronico"],
    )
    
    try:
        cursor.execute(sql, values)
        db.commit()
        print("Alumno insertado correctamente.")
    except Exception as e:
        print("Error al insertar:", e)
        db.rollback()


def BorrarDatos(db,asignatura):
    cursor=db.cursor()


    sql1 = '''DELETE FROM DEPARTAMENTO_ASIGNATURA
            WHERE ID_ASIGNATURA = (SELECT ID_ASIGNATURA
                                    FROM ASIGNATURA
                                    WHERE Nombre = '%s')'''
    

    sql2 = '''DELETE FROM ASIGNATURA_TITULACION
            WHERE ID_ASIGNATURA = (SELECT ID_ASIGNATURA
                                    FROM ASIGNATURA
                                    WHERE Nombre = '%s')'''



    sql3 = '''DELETE FROM ASIGNATURA_ALUMNO
            WHERE ID_ASIGNATURA = (SELECT ID_ASIGNATURA
                                    FROM ASIGNATURA
                                    WHERE Nombre = '%s')'''
    
    sql4 = '''
            DELETE FROM ASIGNATURA
            WHERE Nombre = '%s' '''
    try:
        cursor.execute(sql1 % asignatura)
        cursor.execute (sql2 % asignatura)
        cursor.execute(sql3 % asignatura)
        cursor.execute(sql4 % asignatura)
        print("Datos borrados.")
        db.commit()
    except Exception as e:
        print("Error al borrar datos.", e)
        db.rollback()

def Aumento_Sueldo(db):
    cursor = db.cursor()
    try:
        sueldo = float(input("Introduce un sueldo: "))
        porcentaje = float(input("Introduce un porcentaje: "))
        sueldo_nuevo = sueldo * (1 + porcentaje / 100)
    
        sql = '''
        UPDATE PROFESOR
        SET Sueldo = %s
        WHERE Sueldo < %s
        '''
    
        cursor.execute(sql, (sueldo_nuevo, sueldo))
        db.commit()
        print("Sueldo actualizado.")
    except Exception as e:
        print("Error al actualizar:", e)
        db.rollback()


def MostrarMenu():
    print('''
    1. Listar asignaturas y nº de alumnos que hay en cada una.
    2. Pide dos valores (sueldo mensual) para mostrar el nombre de los profesores que están entre esos dos sueldos.
    3. Pide el nombre de una asignatura y muestra los alumnos que la han aprobado.
    4. Introduce un nuevo alumno.
    5. Pide una asignatura y borra sus datos.
    6. Pide un sueldo y un porcentaje y aumenta ese porcentaje a los profesores que cobren menos que ese sueldo.
    0. SALIR
    ''')


# Inicialización de la conexión a la base de datos
datos = Conectar_BD("localhost", "alejandro", "alejandro", "proyecto")

num = 9
while num != 0:
    MostrarMenu()
    num = int(input("Ingresa una opción: "))

    if num == 1:
        Listar_Asignaturas(datos)
    elif num == 2:
        Sueldo_Profes(datos)
    elif num ==3:
        Alumnos_Asignatura(datos)
    elif num == 4:
        nuevoalumno={
            "Num_Expediente": int(input("Número de Expediente: ")),
            "DNI": input("DNI: "),
            "Nombre": input("Nombre: "),
            "Apellido_Paterno": input("Apellido Paterno: "),
            "Apellido_Materno": input("Apellido Materno: "),
            "Direccion": input("Dirección: "),
            "ID_Grupo": int(input("ID de Grupo: ")),
            "Correo_Electronico": input("Correo Electrónico: ")
        }
        Nuevo_Alumno(datos,nuevoalumno)
    elif num == 5:
        asig = input("Introduce una asignatura para borrar: ")
        BorrarDatos(datos,asig)
    
    elif num == 6:
        Aumento_Sueldo(datos)

    elif num == 0:
        print("Saliendo...")
        print("\n\nHas salido con éxito")

    else:
        print("El número introducido no es una opción.")

# Desconexión de la base de datos al finalizar
Desconectar_BD(datos)
