import cx_Oracle
import sys

def Conectar_BD(usuario, password, dsn):
    try:
        db = cx_Oracle.connect(usuario, password, dsn)
        return db
    except cx_Oracle.Error as e:
        print("No puedo conectar a la base de datos:", e)
        sys.exit(1)

def Desconectar_BD(db):
    db.close()

def Menu():
    print('''
    1. Listar asignaturas y nº de alumnos que hay en cada una.
    2. Pide dos valores (sueldo mensual) para mostrar el nombre de los profesores que están entre esos dos sueldos.
    3. Pide el nombre de una asignatura y muestra los alumnos que la han aprobado.
    4. Introduce un nuevo alumno.
    5. Pide una asignatura y borra sus datos.
    6. Pide un sueldo y un porcentaje y aumenta ese porcentaje a los profesores que cobren menos que ese sueldo.
    0. SALIR
    ''')

# Define las funciones aquí directamente o copia el contenido de funciones.py
def ListarAsignaturas(db):
    cursor = db.cursor()
    sql = '''
    SELECT A.Nombre AS ASIGNATURA, COUNT(AA.ID_ASIGNATURA) AS ALUMNOS
    FROM ASIGNATURA_ALUMNO AA
    JOIN ASIGNATURA A ON AA.ID_ASIGNATURA = A.ID_ASIGNATURA
    GROUP BY A.Nombre  
    '''
    try:
        cursor.execute(sql)
        registros = cursor.fetchall()
        print("{:<20} {:<10}".format("ASIGNATURA", "ALUMNOS"))
        print("-" * 30)
        for registro in registros:
            print("{:<25} {:<10}".format(registro[0], registro[1]))
    except cx_Oracle.Error as e:
        print("Error en la consulta:", e)

def SueldoProfes(db):
        sueldominimo = float(input("Introduce el sueldo minimo:  "))
        sueldomaximo = float(input("Introduce el sueldo máximo:  "))
        sql = ''' SELECT Nombre
                FROM PROFESOR
                WHERE sueldo BETWEEN %s AND %s''' % (sueldominimo,sueldomaximo)
        cursor = db.cursor()
        try:
                cursor.execute(sql)
                registros = cursor.fetchall()
                print("-"*20)
                print("{:<20}".format("Nombre profesor"))
                print("-"*20)
                for registro in registros:
                        print("-{:<20}".format(registro[0]))
        except MySQLdb.Error as e:
                print("Error en la consulta:", e)
        if cursor.rowcount == 0:
                print("\nNo hay profesores entre esos sueldos")

def AlumnosAsignatura(db):
        asig=input("Introduce una asignatura: ")
        sql='''
        SELECT A.Nombre AS ALUMNO
        FROM ALUMNO A, ASIGNATURA_ALUMNO AA, ASIGNATURA ASIG
        WHERE A.Num_Expediente = AA.Num_Expediente AND ASIG.ID_ASIGNATURA = AA.ID_ASIGNATURA
        AND Nota >= 5 AND ASIG.Nombre = :asig
        '''

        cursor=db.cursor()
    
        try:
                cursor.execute(sql, (asig,))
                registros=cursor.fetchall()

                if len(registros)==0:
                        print("No hay datos para mostrar.")
                if len(registros) > 0:
                        print("Alumnos aprobados")
                        print("-"*20)
                        for registro in registros:
                                print (registro[0])
        except Exception as e:
                print("Error en la consulta", e)
def Nuevo_Alumno(db, ALUMNO):
    cursor = db.cursor()
    sql = "INSERT INTO ALUMNO (Num_Expediente, DNI, Nombre, Apellido_Paterno, Apellido_Materno, Direccion, ID_Grupo, Correo_Electronico) VALUES (:num_exp, :dni, :nombre, :apellido_paterno, :apellido_materno, :direccion, :id_grupo, :correo_electronico)"
    
    values = {
        'num_exp': ALUMNO["Num_Expediente"],
        'dni': ALUMNO["DNI"],
        'nombre': ALUMNO["Nombre"],
        'apellido_paterno': ALUMNO["Apellido_Paterno"],
        'apellido_materno': ALUMNO["Apellido_Materno"],
        'direccion': ALUMNO["Direccion"],
        'id_grupo': ALUMNO["ID_Grupo"],
        'correo_electronico': ALUMNO["Correo_Electronico"]
    }

    try:
        cursor.execute(sql, values)
        db.commit()
        print("Alumno insertado correctamente.")
    except Exception as e:
        print("Error al insertar.", e)
        db.rollback()
def BorrarDatos(db, asignatura):
    cursor = db.cursor()
    
    # Borra de la tabla Departamento_Asignatura
    sql1 = '''DELETE FROM DEPARTAMENTO_ASIGNATURA
              WHERE ID_ASIGNATURA = (SELECT ID_ASIGNATURA
                                      FROM ASIGNATURA
                                      WHERE Nombre = :asig)'''

    # Borra de la tabla ASIGNATURA_TITULACION
    sql2 = '''DELETE FROM ASIGNATURA_TITULACION
              WHERE ID_ASIGNATURA = (SELECT ID_ASIGNATURA
                                      FROM ASIGNATURA
                                      WHERE Nombre = :asig)'''

    # Borra de la tabla asignatura_alumno
    sql3 = '''DELETE FROM ASIGNATURA_ALUMNO
              WHERE ID_ASIGNATURA = (SELECT ID_ASIGNATURA
                                      FROM ASIGNATURA
                                      WHERE Nombre = :asig)'''

    # Borra de la tabla asignatura
    sql4 = '''DELETE FROM ASIGNATURA
              WHERE Nombre = :asig'''

    try:
        cursor.execute(sql1, asig=asignatura)
        cursor.execute(sql2, asig=asignatura)
        cursor.execute(sql3, asig=asignatura)
        cursor.execute(sql4, asig=asignatura)
        print("Datos borrados.")
        db.commit()
    except Exception as e:
        print("Error al borrar datos.", e)
        db.rollback()


def AumentoSueldo (db):
        cursor = db.cursor()
        try: 
                sueldo = float(input("Introduce un sueldo:  "))
                porcentaje = float(input("Introduce un porcentaje:  "))
                sueldonuevo = sueldo * (1+porcentaje/100)

                sql = '''UPDATE PROFESOR
                        SET Sueldo = :sueldonuevo
                        WHERE Sueldo < :sueldo
                '''
                cursor.execute(sql, sueldonuevo=sueldonuevo, sueldo=sueldo)
                db.commit()
                print("Sueldo actualizado")
        except Exception as e:
                print("Error al actualizar",e)
                db.rollback()

cx_Oracle.init_oracle_client(lib_dir=r"C:\Users\aleal\oracle\instantclient_21_13")
db = cx_Oracle.connect('alejandro/alejandro@localhost:1521/XE')
num = 9
while num!=0:
        Menu()
        num = int(input("Introduce una opcion: "))
        if num == 1:
                ListarAsignaturas(db)
        if num == 2:
                SueldoProfes(db)
        if num == 3:
                AlumnosAsignatura(db)
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
                Nuevo_Alumno(db,nuevoalumno)
        elif num == 5:
                asig = input("Introduce una asignatura para borrar: ")
                BorrarDatos(db,asig)
        elif num == 6:
                AumentoSueldo(db)

