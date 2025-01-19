import sqlite3
import os

def create_database(company_name):
    """Crea una base de datos para la empresa."""
    db_path = f"database/{company_name}.db"
    
    # Verifica si la base de datos ya existe
    if os.path.exists(db_path):
        print("La base de datos ya existe.")
        return False

    # Crea una nueva base de datos y sus tablas
    conn = sqlite3.connect(db_path)
    create_tables(conn)
    conn.close()
    print(f"Base de datos creada para {company_name}")
    return True


def create_tables(conn):
    """Crea todas las tablas necesarias para el CRM."""
    cursor = conn.cursor()

    # Tabla de identificación
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS IDENTIFICACION (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            NOMBRE_EMPRESA TEXT UNIQUE,
            PASSWORD TEXT,
            MAIL TEXT,
            DIRECCION TEXT,
            TELEFONO TEXT
        )
    ''')

    # Tabla de clientes
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS CLIENTES (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            CIF TEXT UNIQUE,
            NOMBRE TEXT,
            DIRECCION TEXT,
            TELEFONO TEXT,
            CONTACTO TEXT,
            EMAIL TEXT
        )
    ''')

    # Tabla de oportunidades
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS OPORTUNIDADES (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            NOMBRE_OPORTUNIDAD TEXT,
            CLIENTE TEXT,
            FECHA TEXT,
            PRESUPUESTO REAL,
            INGRESO_ESPERADO REAL,
            ESTADO TEXT
        )
    ''')

    # Tabla de presupuestos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS PRESUPUESTOS (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            NOMBRE TEXT,
            FECHA_CREACION TEXT,
            FECHA_EXPIRACION TEXT,
            CLIENTE TEXT,
            SUBTOTAL REAL,
            TOTAL REAL
        )
    ''')

    # Tabla de productos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS PRODUCTOS (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            NOMBRE TEXT,
            PROVEEDOR TEXT,
            DESCRIPCION TEXT,
            IVA REAL,
            PRECIO REAL,
            STOCK INTEGER
        )
    ''')

    # Tabla intermedia para presupuestos y productos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS DETALLE_PRESUPUESTOS (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            PRESUPUESTO_ID INTEGER,
            PRODUCTO_ID INTEGER,
            CANTIDAD INTEGER,
            PRECIO REAL,
            SUBTOTAL REAL,
            FOREIGN KEY (PRESUPUESTO_ID) REFERENCES PRESUPUESTOS(ID),
            FOREIGN KEY (PRODUCTO_ID) REFERENCES PRODUCTOS(ID)
        )
    ''')
    conn.commit()


def insert_company(company_name, password, email):
    """Inserta los datos de la empresa en la tabla IDENTIFICACION."""
    db_path = f"database/{company_name}.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        cursor.execute('''
            INSERT INTO IDENTIFICACION (NOMBRE_EMPRESA, PASSWORD, MAIL)
            VALUES (?, ?, ?)
        ''', (company_name, password, email))
        conn.commit()
        print("Empresa registrada correctamente.")
    except sqlite3.IntegrityError:
        print("Error: La empresa ya está registrada.")
    finally:
        conn.close()


def connect_database(db_name):
    """Conecta a una base de datos existente."""
    conn = sqlite3.connect(db_name)
    return conn


def add_cliente(conn, cif, nombre, direccion, telefono, contacto, email):
    """Agrega un cliente a la base de datos."""
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO CLIENTES (CIF, NOMBRE, DIRECCION, TELEFONO, CONTACTO, EMAIL)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (cif, nombre, direccion, telefono, contacto, email))
    conn.commit()

def update_cliente(conn, id_cliente, cif, nombre, direccion, telefono, contacto, email):
    """Actualiza los datos de un cliente existente."""
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE CLIENTES
        SET CIF = ?, NOMBRE = ?, DIRECCION = ?, TELEFONO = ?, CONTACTO = ?, EMAIL = ?
        WHERE ID = ?
    ''', (cif, nombre, direccion, telefono, contacto, email, id_cliente))
    conn.commit()

def delete_cliente(conn, id_cliente):
    """Elimina un cliente de la base de datos."""
    cursor = conn.cursor()
    cursor.execute('DELETE FROM CLIENTES WHERE ID = ?', (id_cliente,))
    conn.commit()


def add_opportunity(conn, nombre_oportunidad, cliente, fecha, presupuesto, ingreso_esperado, estado):
    """Agrega una oportunidad a la tabla OPORTUNIDADES."""
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO OPORTUNIDADES (NOMBRE_OPORTUNIDAD, CLIENTE, FECHA, PRESUPUESTO, INGRESO_ESPERADO, ESTADO)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (nombre_oportunidad, cliente, fecha, presupuesto, ingreso_esperado, estado))
    conn.commit()


def add_producto(conn, nombre, proveedor, descripcion, iva, precio, stock):
    """Agrega un producto a la tabla PRODUCTOS."""
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO PRODUCTOS (NOMBRE, PROVEEDOR, DESCRIPCION, IVA, PRECIO, STOCK)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (nombre, proveedor, descripcion, iva, precio, stock))
    conn.commit()

def update_producto(conn, id_producto, nombre, proveedor, descripcion, iva, precio, stock):
    """Actualiza los datos de un producto existente."""
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE PRODUCTOS
        SET NOMBRE = ?, PROVEEDOR = ?, DESCRIPCION = ?, IVA = ?, PRECIO = ?, STOCK = ?
        WHERE ID = ?
    ''', (nombre, proveedor, descripcion, iva, precio, stock, id_producto))
    conn.commit()

def delete_producto(conn, id_producto):
    """Elimina un producto de la base de datos."""
    cursor = conn.cursor()
    cursor.execute('DELETE FROM PRODUCTOS WHERE ID = ?', (id_producto,))
    conn.commit()
    

def add_presupuesto(conn, nombre, fecha_creacion, fecha_expiracion, cliente, subtotal, total):
    """Agrega un presupuesto a la tabla PRESUPUESTOS."""
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO PRESUPUESTOS (NOMBRE, FECHA_CREACION, FECHA_EXPIRACION, CLIENTE, SUBTOTAL, TOTAL)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (nombre, fecha_creacion, fecha_expiracion, cliente, subtotal, total))
    conn.commit()
