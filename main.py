from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt5 import QtWidgets
from src.login_ui import Ui_MainWindow  # Interfaz del login
from src.main_window_ui import Ui_MainWindow as Ui_MainApp  # Interfaz de la ventana principal
from src.database import *
from PyQt5 import QtCore
from PyQt5.QtGui import QPixmap
import os
import sqlite3



class MainWindow(QMainWindow):
    def __init__(self, company_name, empresa_data):
        super().__init__()
        self.ui = Ui_MainApp()
        self.ui.setupUi(self)
        self.company_name = company_name
        self.db_path = f"database/{self.company_name}.db"

        # Muestra un mensaje de bienvenida con el nombre de la empresa
        self.ui.label_welcome.setText(f"¡ Bienvenido/a al CRM, {self.company_name} !")

        # Conectar botones de la ventana principal con las páginas del QStackedWidget
        self.ui.btn_pipeline.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.page_pipeline))
        self.ui.btn_empresa.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.page_empresa))
        self.ui.btn_clientes.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.page_clientes))
        self.ui.btn_oportunidades.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.page_oportunidades))
        self.ui.btn_presupuestos.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.page_presupuetos))
        self.ui.btn_inventario.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.page_inventario))


        # Conectar botones del módulo Clientes
        self.ui.nuevo_cliente_btn_crear_nuevo_cliente.clicked.connect(self.nuevo_cliente)
        self.ui.clientes_btn_editar_cliente.clicked.connect(self.editar_cliente)
        self.ui.clientes_btn_eliminar_cliente.clicked.connect(self.eliminar_cliente)

        # Llenar los campos de la página empresa
        self.ui.empresa_nombre_empresa.setText(empresa_data[0])  # Nombre de la empresa
        self.ui.empresa_correo_electronico.setText(empresa_data[1])  # Email
        self.ui.empresa_direccion.setText(empresa_data[2])  # Dirección
        self.ui.empresa_telefono.setText(empresa_data[3])  # Teléfono
        # Conectar el botón para guardar cambios
        self.ui.empresa_btn_guardar_cambios.clicked.connect(self.guardar_cambios_empresa)

        # Conectar botones del módulo Inventario
        self.ui.nuevo_producto_btn_crear_nuevo_producto.clicked.connect(self.crear_nuevo_producto)
        self.ui.inventario_btn_editar_producto.clicked.connect(self.editar_producto)
        self.ui.inventario_btn_eliminar_producto.clicked.connect(self.eliminar_producto)
        
        # Conectar botones del módulo presupuestos
        self.configurar_nuevo_presupuesto()
        self.configurar_presupuestos()
        self.ui.presupuestos_btn_eliminar_presupuesto.clicked.connect(self.eliminar_presupuesto)
        self.ui.presupuestos_btn_editar_presupuesto.clicked.connect(self.editar_presupuesto)

        # Conectar botones del módulo oportunidades
        self.configurar_formulario_nueva_oportunidad()
        self.ui.nueva_oportunidad_btn_crear_nueva_oportunidad.clicked.connect(self.crear_nueva_oportunidad)
        self.ui.oportunidades_btn_editar_oportunidad.clicked.connect(self.editar_oportunidad)
        self.ui.oportunidades_btn_eliminar_oportunidad.clicked.connect(self.eliminar_oportunidad)

        # Conectar botones del Pipeline
        self.ui.btn_mover_fase_siguiente.clicked.connect(self.mover_fase_siguiente)
        self.ui.btn_mover_fase_anterior.clicked.connect(self.mover_fase_anterior)
        # Configurar el logo, imagen CRM
        self.configurar_logo()
        # Conectar el botón de cerrar sesión
        self.ui.btn_logout.clicked.connect(self.cerrar_sesion)


        # Cargar datos iniciales
        self.load_pipeline()
        self.cargar_clientes()
        self.cargar_productos()
        self.cargar_clientes_combo()
        self.cargar_productos_combo()
        self.cargar_oportunidades()
        self.cargar_pipeline()
        

    def connect_db(self):
        """Conecta a la base de datos de la empresa."""
        return sqlite3.connect(self.db_path)

    def load_pipeline(self):
        """Carga las oportunidades en las listas del Pipeline."""
        conn = self.connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM OPORTUNIDADES")
        opportunities = cursor.fetchall()
        conn.close()

        # Limpiar las listas
        self.ui.list_nuevo.clear()
        self.ui.list_calificado.clear()
        self.ui.list_propuesta.clear()
        self.ui.list_ganado.clear()

        # Llenar las listas
        for opp in opportunities:
            item_text = f"{opp[1]} - {opp[2]}"  # Nombre de la oportunidad y cliente
            if opp[6] == "Nuevo":
                self.ui.list_nuevo.addItem(item_text)
            elif opp[6] == "Calificado":
                self.ui.list_calificado.addItem(item_text)
            elif opp[6] == "Propuesta":
                self.ui.list_propuesta.addItem(item_text)
            elif opp[6] == "Ganado":
                self.ui.list_ganado.addItem(item_text)

    # Métodos de CLIENTE
    def nuevo_cliente(self):
        """Extrae datos de la UI y los pasa a la función para insertar un cliente."""
        
        cif = self.ui.nuevo_cliente_cif.text()  # Capturar el CIF desde el campo de texto
        nombre = self.ui.nuevo_cliente_nombre.text()
        direccion = self.ui.nuevo_cliente_direccion.text()
        telefono = self.ui.nuevo_cliente_telefono.text()
        contacto = self.ui.nuevo_cliente_contacto.text()
        email = self.ui.nuevo_cliente_email.text()

        # Verificar que no haya campos vacíos
        if not cif or not nombre or not direccion or not telefono or not contacto or not email:
            QMessageBox.warning(self, "Error", "Por favor, completa todos los campos.")
            return

        # Conectar a la base de datos y guardar el cliente
        conn = self.connect_db()
        try:
            add_cliente(conn, cif, nombre, direccion, telefono, contacto, email)  # Pasamos el CIF y demás parámetros
            QMessageBox.information(self, "Éxito", "Cliente agregado correctamente.")
            self.cargar_clientes()  # Refrescar la tabla de clientes
            self.limpiar_formulario_cliente() # Limpiar el formulario
            self.cargar_clientes_combo_oportunidades()
            self.cargar_clientes_combo()#combo de nuevo presupuesto
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Error", "El cliente ya existe.")
        finally:
            conn.close()
        
        """Lógica para agregar un nuevo cliente."""
        """""
        conn = self.connect_db()
        add_cliente(conn, "12345678C", "Cliente X", "Calle Falsa 123", "555-555-555", "Contacto X", "cliente@example.com")
        conn.close()
        QMessageBox.information(self, "Éxito", "Cliente agregado correctamente.")
        # Aquí puedes recargar la tabla de clientes.
        self.cargar_clientes()
        """
    def limpiar_formulario_cliente(self):
        """Limpia los campos del formulario de nuevo cliente."""
        self.ui.nuevo_cliente_cif.clear()
        self.ui.nuevo_cliente_nombre.clear()
        self.ui.nuevo_cliente_direccion.clear()
        self.ui.nuevo_cliente_telefono.clear()
        self.ui.nuevo_cliente_contacto.clear()
        self.ui.nuevo_cliente_email.clear()
    
    def editar_cliente(self):
        """Edita un cliente seleccionado."""
        # Obtener cliente seleccionado en la tabla
        current_row = self.ui.clientes_tabla.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Error", "Por favor, selecciona un cliente.")
            return

        # Extraer datos de la fila seleccionada
        id_cliente = int(self.ui.clientes_tabla.item(current_row, 0).text())  # ID en la columna 0
        cif = self.ui.clientes_tabla.item(current_row, 1).text()  # CIF en la columna 1
        nombre = self.ui.clientes_tabla.item(current_row, 2).text()  # Nombre en la columna 2
        direccion = self.ui.clientes_tabla.item(current_row, 3).text()  # Dirección en la columna 3
        telefono = self.ui.clientes_tabla.item(current_row, 4).text()  # Teléfono en la columna 4
        contacto = self.ui.clientes_tabla.item(current_row, 5).text()  # Contacto en la columna 5
        email = self.ui.clientes_tabla.item(current_row, 6).text()  # Email en la columna 6

        # Validar datos
        if not cif or not nombre or not direccion or not telefono or not contacto or not email:
            QMessageBox.warning(self, "Error", "Por favor, completa todos los campos.")
            return

        # Actualizar en la base de datos
        conn = self.connect_db()
        try:
            update_cliente(conn, id_cliente, cif, nombre, direccion, telefono, contacto, email)
            QMessageBox.information(self, "Éxito", "Cliente actualizado correctamente.")
            self.cargar_clientes()  # Refrescar tabla
            self.cargar_clientes_combo_oportunidades()
            self.cargar_clientes_combo()#combo de nuevo presupuesto
        finally:
            conn.close()
        
        """Lógica para editar un cliente."""
        """
        conn = self.connect_db()
        update_cliente(conn, 2, "CIF12345", "Cliente Editado", "Nueva Dirección", "666-666-666", "Nuevo Contacto", "nuevoemail@example.com")
        conn.close()
        QMessageBox.information(self, "Éxito", "Cliente editado correctamente.")
        self.cargar_clientes()"""

    def eliminar_cliente(self):
        """Elimina un cliente seleccionado."""
        current_row = self.ui.clientes_tabla.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Error", "Por favor, selecciona un cliente.")
            return

        id_cliente = self.ui.clientes_tabla.item(current_row, 0).text()  # Primera columna: ID

        # Crear cuadro de confirmación
        confirm = QMessageBox(self)
        confirm.setIcon(QMessageBox.Question)
        confirm.setWindowTitle("Confirmar Eliminación")
        confirm.setText(f"¿Estás seguro de eliminar el cliente con ID {id_cliente}?")
        confirm.setStandardButtons(QMessageBox.Yes | QMessageBox.No)

        # Personalizar los botones
        button_yes = confirm.button(QMessageBox.Yes)
        button_yes.setText("Sí")
        button_no = confirm.button(QMessageBox.No)
        button_no.setText("No")

        # Mostrar el cuadro de confirmación
        confirm.exec_()

        # Verificar la respuesta
        if confirm.clickedButton() == button_yes:
            conn = self.connect_db()
            try:
                delete_cliente(conn, id_cliente)
                QMessageBox.information(self, "Éxito", "Cliente eliminado correctamente.")
                self.cargar_clientes()  # Refrescar tabla
                self.cargar_clientes_combo_oportunidades()
                self.cargar_clientes_combo()#combo de nuevo presupuesto
            finally:
                conn.close()
        
        """Lógica para eliminar un cliente."""
        """conn = self.connect_db()
        delete_cliente(conn, 2)
        conn.close()
        QMessageBox.information(self, "Éxito", "Cliente eliminado correctamente.")
        # Aquí puedes recargar la tabla de clientes.
        self.cargar_clientes()"""

    def cargar_clientes(self):
        """Carga los clientes desde la base de datos y los muestra en la tabla."""
        conn = self.connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM CLIENTES")
        clientes = cursor.fetchall()
        conn.close()

        # Limpiar la tabla
        self.ui.clientes_tabla.setRowCount(0)

        # Llenar la tabla con datos
        for row_num, cliente in enumerate(clientes):
            self.ui.clientes_tabla.insertRow(row_num)
            for col_num, data in enumerate(cliente):
                item = QtWidgets.QTableWidgetItem(str(data))
                if col_num in [0, 1]:  # ID y CIF no editables
                    item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEditable)
                self.ui.clientes_tabla.setItem(row_num, col_num, item)

                

    # Métodos de EMPRESA
    def guardar_cambios_empresa(self):
        """Guarda los cambios realizados en los datos de la empresa."""
        # Obtener los valores de los campos
        nuevo_email = self.ui.empresa_correo_electronico.text()
        nueva_direccion = self.ui.empresa_direccion.text()
        nuevo_telefono = self.ui.empresa_telefono.text()

        # Validar que no estén vacíos
        if not nuevo_email or not nueva_direccion or not nuevo_telefono:
            QMessageBox.warning(self, "Error", "Por favor, completa todos los campos.")
            return

        # Actualizar la base de datos
        conn = sqlite3.connect(f"database/{self.company_name}.db")
        cursor = conn.cursor()
        try:
            cursor.execute('''
                UPDATE IDENTIFICACION
                SET MAIL = ?, DIRECCION = ?, TELEFONO = ?
                WHERE NOMBRE_EMPRESA = ?
            ''', (nuevo_email, nueva_direccion, nuevo_telefono, self.company_name))
            conn.commit()
            QMessageBox.information(self, "Éxito", "Datos actualizados correctamente.")
        except sqlite3.IntegrityError as e:
            QMessageBox.warning(self, "Error", f"No se pudo actualizar: {e}")
        finally:
            conn.close()

    def crear_nuevo_producto(self):
        """Valida y crea un nuevo producto."""
        nombre = self.ui.nuevo_producto_nombre_producto.text()
        proveedor = self.ui.nuevo_producto_nombre_proveedor.text()
        #descripcion = self.ui.nuevo_producto_descripcion.toPlainText()  # Si es QTextEdit
        descripcion = self.ui.nuevo_producto_descripcion.text()
        iva = self.ui.nuevo_producto_iva.text()
        precio = self.ui.nuevo_producto_precio.text()
        stock = self.ui.nuevo_producto_stock.text()

        # Validar campos
        if not nombre or not proveedor or not descripcion or not iva or not precio or not stock:
            QMessageBox.warning(self, "Error", "Por favor, completa todos los campos.")
            return

        if not iva.replace('.', '', 1).isdigit() or not precio.replace('.', '', 1).isdigit() or not stock.isdigit():
            QMessageBox.warning(self, "Error", "IVA, precio y stock deben ser valores numéricos.")
            return

        # Conectar a la base de datos y guardar el producto
        conn = self.connect_db()
        try:
            add_producto(conn, nombre, proveedor, descripcion, float(iva), float(precio), int(stock))
            QMessageBox.information(self, "Éxito", "Producto agregado correctamente.")
            self.cargar_productos()  # Refrescar la tabla de inventario
            self.limpiar_campos_producto()  # Limpiar campos tras éxito
            self.cargar_productos_combo() # combo nuevo presupuesto
        except sqlite3.IntegrityError as e:
            QMessageBox.warning(self, "Error", f"No se pudo agregar el producto: {e}")
        finally:
            conn.close()

    def editar_producto(self):
        """Edita un producto seleccionado."""
        current_row = self.ui.inventario_tabla_inventario.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Error", "Por favor, selecciona un producto.")
            return

        # Obtener datos de la fila seleccionada
        id_producto = int(self.ui.inventario_tabla_inventario.item(current_row, 0).text())  # ID en la columna 0
        nombre = self.ui.inventario_tabla_inventario.item(current_row, 1).text()  # Nombre
        proveedor = self.ui.inventario_tabla_inventario.item(current_row, 2).text()  # Proveedor
        descripcion = self.ui.inventario_tabla_inventario.item(current_row, 3).text()  # Descripción
        iva = self.ui.inventario_tabla_inventario.item(current_row, 4).text()  # IVA
        precio = self.ui.inventario_tabla_inventario.item(current_row, 5).text()  # Precio
        stock = self.ui.inventario_tabla_inventario.item(current_row, 6).text()  # Stock

        # Validar campos vacíos
        if not nombre or not proveedor or not descripcion or not iva or not precio or not stock:
            QMessageBox.warning(self, "Error", "Por favor, completa todos los campos.")
            return

        # Validar que IVA, Precio y Stock sean valores numéricos válidos
        try:
            iva = float(iva)
            if iva < 0:
                raise ValueError("El IVA no puede ser negativo.")

            precio = float(precio)
            if precio < 0:
                raise ValueError("El precio no puede ser negativo.")

            stock = int(stock)
            if stock < 0:
                raise ValueError("El stock no puede ser negativo.")
        except ValueError as e:
            QMessageBox.warning(self, "Error", f"Error en los datos numéricos: IVA, Precio y Stock deben ser números positivos. Stock número entero sin decimales.")
            return

        # Crear un QMessageBox con botones personalizados
        confirm = QMessageBox(self)
        confirm.setIcon(QMessageBox.Question)
        confirm.setWindowTitle("Confirmar Edición")
        confirm.setText(f"¿Guardar los cambios en el producto '{nombre}'?")
        btn_si = confirm.addButton("Sí", QMessageBox.YesRole)
        btn_no = confirm.addButton("No", QMessageBox.NoRole)
        confirm.setDefaultButton(btn_no)
        confirm.exec_()

        if confirm.clickedButton() == btn_si:
            try:
                # Actualizar el producto en la base de datos
                conn = self.connect_db()
                update_producto(conn, id_producto, nombre, proveedor, descripcion, iva, precio, stock)
                QMessageBox.information(self, "Éxito", "Producto actualizado correctamente.")
                self.cargar_productos()  # Refrescar tabla
                self.cargar_productos_combo()  # Refrescar combo para presupuestos
            except sqlite3.Error as e:
                QMessageBox.warning(self, "Error", f"No se pudo actualizar el producto: {e}")
            finally:
                conn.close()



    def eliminar_producto(self):
        """Elimina un producto seleccionado."""
        current_row = self.ui.inventario_tabla_inventario.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Error", "Por favor, selecciona un producto.")
            return

        id_producto = int(self.ui.inventario_tabla_inventario.item(current_row, 0).text())  # ID en la columna 0

        # Crear cuadro de confirmación
        confirm = QMessageBox(self)
        confirm.setIcon(QMessageBox.Question)
        confirm.setWindowTitle("Confirmar Eliminación")
        confirm.setText(f"¿Estás seguro de eliminar el producto con ID {id_producto}?")
        confirm.setStandardButtons(QMessageBox.Yes | QMessageBox.No)

        # Personalizar botones
        button_yes = confirm.button(QMessageBox.Yes)
        button_yes.setText("Sí")
        button_no = confirm.button(QMessageBox.No)
        button_no.setText("No")

        # Mostrar el cuadro de confirmación
        confirm.exec_()

        # Verificar qué botón fue presionado
        if confirm.clickedButton() == button_yes:
            conn = self.connect_db()
            try:
                delete_producto(conn, id_producto)
                QMessageBox.information(self, "Éxito", "Producto eliminado correctamente.")
                self.cargar_productos()
                self.cargar_productos_combo() # combo nuevo presupuesto
            finally:
                conn.close()

    def limpiar_campos_producto(self):
        """Limpia los campos del formulario de creación de producto."""
        self.ui.nuevo_producto_nombre_producto.clear()
        self.ui.nuevo_producto_nombre_proveedor.clear()
        self.ui.nuevo_producto_descripcion.clear()  # Si es QLineEdit
        # Si fuera QTextEdit: self.ui.nuevo_producto_descripcion.setPlainText("")
        self.ui.nuevo_producto_iva.clear()
        self.ui.nuevo_producto_precio.clear()
        self.ui.nuevo_producto_stock.clear()

    def cargar_productos(self):
        """Carga los productos desde la base de datos y los muestra en la tabla."""
        conn = self.connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM PRODUCTOS")
        productos = cursor.fetchall()
        conn.close()

        # Limpiar la tabla
        self.ui.inventario_tabla_inventario.setRowCount(0)

        # Llenar la tabla con datos
        for row_num, producto in enumerate(productos):
            self.ui.inventario_tabla_inventario.insertRow(row_num)
            for col_num, data in enumerate(producto):
                item = QtWidgets.QTableWidgetItem(str(data))

                # Hacer la primera columna (ID) de solo lectura
                if col_num == 0:  # Columna 0 es la columna del ID
                    item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEditable)

                # Agregar el ítem a la tabla
                self.ui.inventario_tabla_inventario.setItem(row_num, col_num, item)

    def configurar_nuevo_presupuesto(self):
        """Configura la página para crear un nuevo presupuesto."""
        # Configurar fecha de creación por defecto
        self.ui.nuevo_presupuesto_fecha_creacion.setDate(QtCore.QDate.currentDate())
        self.ui.nuevo_presupuesto_fecha_expiracion.setDate(QtCore.QDate.currentDate().addDays(30))

        # Cargar clientes en el combo box
        self.cargar_clientes_combo()

        # Configurar la tabla de productos
        self.ui.nuevo_presupuesto_tabla_productos.setColumnCount(4)
        self.ui.nuevo_presupuesto_tabla_productos.setHorizontalHeaderLabels(["Producto", "Cantidad", "Precio Unitario", "Subtotal"])
        self.ui.nuevo_presupuesto_tabla_productos.setEditTriggers(QtWidgets.QAbstractItemView.AllEditTriggers)

        # Botones
        self.ui.nuevo_presupuesto_btn_agregar_producto.clicked.connect(self.agregar_producto_a_tabla)
        self.ui.nuevo_presupuesto_btn_guardar_presupuesto.clicked.connect(self.guardar_presupuesto)
        self.ui.nuevo_presupuesto_btn_cancelar.clicked.connect(self.cancelar_presupuesto)

    def configurar_presupuestos(self):
        """Configura la página de presupuestos."""
        #tabla presupuestos
        self.ui.presupuestos_tabla_presupuestos.setColumnCount(7)
        self.ui.presupuestos_tabla_presupuestos.setHorizontalHeaderLabels(
            ["ID", "Nombre", "Fecha Creación", "Fecha Expiración", "Cliente", "Subtotal", "Total"]
        )
        #tabla detalles de productos
        self.ui.presupuestos_tabla_detalle_productos.setColumnCount(4)
        self.ui.presupuestos_tabla_detalle_productos.setHorizontalHeaderLabels(
            ["Producto", "Cantidad", "Precio Unitario", "Subtotal"]
        )
        self.ui.presupuestos_tabla_detalle_productos.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)  # Desactivar edición
        #evento para escuchar el click en la tabla presupuestos
        self.ui.presupuestos_tabla_presupuestos.cellClicked.connect(self.mostrar_detalle_presupuesto)
        self.cargar_presupuestos()

    def cargar_clientes_combo(self):
        """Carga los clientes en el combo box."""
        conn = self.connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT ID, NOMBRE FROM CLIENTES")
        clientes = cursor.fetchall()
        conn.close()

        self.ui.nuevo_presupuesto_cliente.clear()
        for cliente in clientes:
            self.ui.nuevo_presupuesto_cliente.addItem(cliente[1], cliente[0])  # Mostrar nombre, almacenar ID

    def agregar_producto_a_tabla(self):
        """Agrega un producto seleccionado a la tabla del presupuesto."""
        self.agregar_producto_desde_combo()

    def guardar_presupuesto(self):
        """Guarda el presupuesto y sus productos en la base de datos."""
        nombre = self.ui.nuevo_presupuesto_nombre.text()
        fecha_creacion = self.ui.nuevo_presupuesto_fecha_creacion.date().toString("yyyy-MM-dd")
        fecha_expiracion = self.ui.nuevo_presupuesto_fecha_expiracion.date().toString("yyyy-MM-dd")
        cliente_id = self.ui.nuevo_presupuesto_cliente.currentData()

        if not nombre or not cliente_id:
            QMessageBox.warning(self, "Error", "Por favor, completa todos los campos.")
            return

        # Calcular subtotal y total con IVA
        subtotal = 0
        total = 0
        for row in range(self.ui.nuevo_presupuesto_tabla_productos.rowCount()):
            producto_id = self.ui.nuevo_presupuesto_tabla_productos.item(row, 0).data(QtCore.Qt.UserRole)
            cantidad = int(self.ui.nuevo_presupuesto_tabla_productos.item(row, 1).text())
            precio = float(self.ui.nuevo_presupuesto_tabla_productos.item(row, 2).text())

            # Consultar el IVA del producto desde la base de datos
            conn = self.connect_db()
            cursor = conn.cursor()
            cursor.execute("SELECT IVA FROM PRODUCTOS WHERE ID = ?", (producto_id,))
            iva_row = cursor.fetchone()
            conn.close()
            if not iva_row:
                QMessageBox.warning(self, "Error", f"No se pudo encontrar el IVA para el producto ID {producto_id}.")
                return

            iva = float(iva_row[0]) / 100
            subtotal_producto = cantidad * precio
            total_producto = subtotal_producto + (subtotal_producto * iva)

            subtotal += subtotal_producto
            total += total_producto
        # Redondeamos para que solo tenga 2 dígitos después de la coma
        subtotal = round(subtotal, 2)
        total = round(total, 2) 
        # Insertar presupuesto
        conn = self.connect_db()
        try:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO PRESUPUESTOS (NOMBRE, FECHA_CREACION, FECHA_EXPIRACION, CLIENTE, SUBTOTAL, TOTAL)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (nombre, fecha_creacion, fecha_expiracion, cliente_id, subtotal, total))
            presupuesto_id = cursor.lastrowid

            # Insertar productos en DETALLE_PRESUPUESTOS
            for row in range(self.ui.nuevo_presupuesto_tabla_productos.rowCount()):
                producto_id = int(self.ui.nuevo_presupuesto_tabla_productos.item(row, 0).data(QtCore.Qt.UserRole))
                cantidad = int(self.ui.nuevo_presupuesto_tabla_productos.item(row, 1).text())
                precio = float(self.ui.nuevo_presupuesto_tabla_productos.item(row, 2).text())
                subtotal_producto = float(self.ui.nuevo_presupuesto_tabla_productos.item(row, 3).text())
                cursor.execute('''
                    INSERT INTO DETALLE_PRESUPUESTOS (PRESUPUESTO_ID, PRODUCTO_ID, CANTIDAD, PRECIO, SUBTOTAL)
                    VALUES (?, ?, ?, ?, ?)
                ''', (presupuesto_id, producto_id, cantidad, precio, subtotal_producto))
            conn.commit()
            QMessageBox.information(self, "Éxito", "Presupuesto creado correctamente.")
            self.cargar_presupuestos()  # Actualizar tabla de presupuestos
            self.limpiar_formulario_presupuesto()
            # Cargar presupuestos en el combo box de oportunidades
            self.cargar_presupuestos_combo_oportunidades()
        except sqlite3.Error as e:
            QMessageBox.warning(self, "Error", f"No se pudo guardar el presupuesto: {e}")
        finally:
            conn.close()


    def limpiar_formulario_presupuesto(self):
        """Limpia los campos del formulario de creación de presupuesto y la tabla de productos."""
        # Limpiar el nombre del presupuesto
        self.ui.nuevo_presupuesto_nombre.clear()
        
        # Restablecer las fechas
        self.ui.nuevo_presupuesto_fecha_creacion.setDate(QtCore.QDate.currentDate())
        self.ui.nuevo_presupuesto_fecha_expiracion.setDate(QtCore.QDate.currentDate().addDays(30))

        # Vaciar la tabla de productos
        self.ui.nuevo_presupuesto_tabla_productos.setRowCount(0)



    def cargar_presupuestos(self):
        """Carga los presupuestos desde la base de datos y los muestra en la tabla."""
        conn = self.connect_db()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                p.ID, 
                p.NOMBRE, 
                p.FECHA_CREACION, 
                p.FECHA_EXPIRACION, 
                c.NOMBRE AS CLIENTE, 
                p.SUBTOTAL, 
                p.TOTAL
            FROM PRESUPUESTOS p
            JOIN CLIENTES c ON p.CLIENTE = c.ID
        ''')
        
        presupuestos = cursor.fetchall()
        conn.close()

        self.ui.presupuestos_tabla_presupuestos.setRowCount(0)

        for row_num, presupuesto in enumerate(presupuestos):
            self.ui.presupuestos_tabla_presupuestos.insertRow(row_num)
            for col_num, data in enumerate(presupuesto):
                item = QtWidgets.QTableWidgetItem(f"{data:.2f}" if isinstance(data, float) else str(data))
                if col_num in [0, 4, 5, 6]:  # ID, Cliente ,Subtotal y Total no editables
                    item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEditable)
                self.ui.presupuestos_tabla_presupuestos.setItem(row_num, col_num, item)


    def cargar_productos_combo(self):
        """Carga los productos en un combo box."""
        conn = self.connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT ID, NOMBRE, PRECIO FROM PRODUCTOS")
        productos = cursor.fetchall()
        conn.close()

        self.ui.nuevo_presupuesto_combo_productos.clear()
        for producto in productos:
            self.ui.nuevo_presupuesto_combo_productos.addItem(f"{producto[1]} - ${producto[2]:.2f}", producto)

    def agregar_producto_desde_combo(self):
        """Agrega un producto desde el combo box a la tabla o actualiza su cantidad si ya existe."""
        producto = self.ui.nuevo_presupuesto_combo_productos.currentData()

        if not producto:
            QtWidgets.QMessageBox.warning(self, "Error", "Por favor, selecciona un producto.")
            return

        producto_id, nombre, precio = producto

        # Verificar si el producto ya está en la tabla
        row_count = self.ui.nuevo_presupuesto_tabla_productos.rowCount()
        for row in range(row_count):
            item_nombre = self.ui.nuevo_presupuesto_tabla_productos.item(row, 0)
            if item_nombre and item_nombre.data(QtCore.Qt.UserRole) == producto_id:
                # Producto encontrado, actualizar cantidad y subtotal
                cantidad_item = self.ui.nuevo_presupuesto_tabla_productos.item(row, 1)
                subtotal_item = self.ui.nuevo_presupuesto_tabla_productos.item(row, 3)

                # Incrementar la cantidad
                cantidad_actual = int(cantidad_item.text())
                nueva_cantidad = cantidad_actual + 1
                cantidad_item.setText(str(nueva_cantidad))

                # Actualizar el subtotal
                nuevo_subtotal = nueva_cantidad * precio
                subtotal_item.setText(f"{nuevo_subtotal:.2f}")

                return  # Salir del método, ya que el producto fue actualizado

        # Si no está en la tabla, agregarlo como nueva fila
        self.ui.nuevo_presupuesto_tabla_productos.insertRow(row_count)

        # Crear el item para el nombre del producto y almacenar el ID en UserRole
        item_nombre = QtWidgets.QTableWidgetItem(nombre)
        item_nombre.setData(QtCore.Qt.UserRole, producto_id)  # Asociar el producto_id con la celda
        item_nombre.setFlags(item_nombre.flags() & ~QtCore.Qt.ItemIsEditable)  # Hacer no editable
        self.ui.nuevo_presupuesto_tabla_productos.setItem(row_count, 0, item_nombre)

        # Rellenar las demás celdas
        self.ui.nuevo_presupuesto_tabla_productos.setItem(row_count, 1, QtWidgets.QTableWidgetItem("1"))  # Cantidad inicial

        item_precio = QtWidgets.QTableWidgetItem(f"{precio:.2f}")
        item_precio.setFlags(item_precio.flags() & ~QtCore.Qt.ItemIsEditable)  # Hacer no editable
        self.ui.nuevo_presupuesto_tabla_productos.setItem(row_count, 2, item_precio)

        item_subtotal = QtWidgets.QTableWidgetItem(f"{precio:.2f}")  # Subtotal inicial
        item_subtotal.setFlags(item_subtotal.flags() & ~QtCore.Qt.ItemIsEditable)  # Hacer no editable
        self.ui.nuevo_presupuesto_tabla_productos.setItem(row_count, 3, item_subtotal)


    def cancelar_presupuesto(self):
        """Descarta los cambios y vuelve a la página de presupuestos con confirmación en español."""
        # Crear el cuadro de confirmación
        confirm = QMessageBox(self)
        confirm.setWindowTitle("Cancelar Presupuesto")
        confirm.setText("¿Estás seguro de que deseas cancelar este presupuesto? Todos los cambios se perderán.")
        confirm.setIcon(QMessageBox.Question)

        # Configurar botones en español
        btn_si = confirm.addButton("Sí", QMessageBox.YesRole)
        btn_no = confirm.addButton("No", QMessageBox.NoRole)

        # Mostrar el cuadro de diálogo
        confirm.exec_()

        # Verificar respuesta
        if confirm.clickedButton() == btn_si:
            # Limpiar el formulario
            self.limpiar_formulario_presupuesto()
            # Volver a la página de presupuestos
            self.ui.stackedWidget.setCurrentWidget(self.ui.page_presupuetos)

    def mostrar_detalle_presupuesto(self, row, column):
        """Carga los productos asociados al presupuesto seleccionado y los muestra en la tabla de detalles."""
        # Obtener el ID del presupuesto seleccionado (columna 0 de la tabla de presupuestos)
        presupuesto_id_item = self.ui.presupuestos_tabla_presupuestos.item(row, 0)
        if not presupuesto_id_item:
            return

        presupuesto_id = int(presupuesto_id_item.text())

        # Obtener los productos asociados desde la base de datos
        conn = self.connect_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT 
                p.NOMBRE, dp.CANTIDAD, dp.PRECIO, dp.SUBTOTAL
            FROM DETALLE_PRESUPUESTOS dp
            JOIN PRODUCTOS p ON dp.PRODUCTO_ID = p.ID
            WHERE dp.PRESUPUESTO_ID = ?
        ''', (presupuesto_id,))
        productos = cursor.fetchall()
        conn.close()

        # Limpiar la tabla de detalles
        self.ui.presupuestos_tabla_detalle_productos.setRowCount(0)

        # Llenar la tabla de detalles con los productos obtenidos
        for row_num, producto in enumerate(productos):
            self.ui.presupuestos_tabla_detalle_productos.insertRow(row_num)
            for col_num, data in enumerate(producto):
                item = QtWidgets.QTableWidgetItem(str(data))
                item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEditable)  # Hacer los campos de solo lectura
                self.ui.presupuestos_tabla_detalle_productos.setItem(row_num, col_num, item)

    def eliminar_presupuesto(self):
        """Elimina el presupuesto seleccionado y sus productos relacionados."""
        current_row = self.ui.presupuestos_tabla_presupuestos.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Error", "Por favor, selecciona un presupuesto.")
            return

        # Obtener el ID del presupuesto seleccionado
        id_presupuesto = int(self.ui.presupuestos_tabla_presupuestos.item(current_row, 0).text())

        # Ventana de confirmación con botones personalizados
        confirm = QMessageBox(self)
        confirm.setWindowTitle("Confirmar Eliminación")
        confirm.setText(f"¿Estás seguro de eliminar el presupuesto con ID {id_presupuesto}?")
        confirm.setIcon(QMessageBox.Question)

        btn_si = confirm.addButton("Sí", QMessageBox.YesRole)
        btn_no = confirm.addButton("No", QMessageBox.NoRole)

        confirm.exec_()

        if confirm.clickedButton() == btn_si:
            conn = self.connect_db()
            try:
                cursor = conn.cursor()
                # Eliminar productos asociados
                cursor.execute("DELETE FROM DETALLE_PRESUPUESTOS WHERE PRESUPUESTO_ID = ?", (id_presupuesto,))
                # Eliminar el presupuesto
                cursor.execute("DELETE FROM PRESUPUESTOS WHERE ID = ?", (id_presupuesto,))
                conn.commit()
                QMessageBox.information(self, "Éxito", "Presupuesto eliminado correctamente.")
                self.cargar_presupuestos()# Recargar la tabla
                # Cargar presupuestos en el combo box de oportunidades
                self.cargar_presupuestos_combo_oportunidades()
            except sqlite3.Error as e:
                QMessageBox.warning(self, "Error", f"No se pudo eliminar el presupuesto: {e}")
            finally:
                conn.close()

    def editar_presupuesto(self):
        """Edita el presupuesto seleccionado en la tabla."""
        current_row = self.ui.presupuestos_tabla_presupuestos.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Error", "Por favor, selecciona un presupuesto.")
            return

        # Obtener el ID del presupuesto seleccionado
        id_presupuesto = int(self.ui.presupuestos_tabla_presupuestos.item(current_row, 0).text())

        # Obtener los nuevos valores de la tabla
        nombre = self.ui.presupuestos_tabla_presupuestos.item(current_row, 1).text()
        fecha_creacion = self.ui.presupuestos_tabla_presupuestos.item(current_row, 2).text()
        fecha_expiracion = self.ui.presupuestos_tabla_presupuestos.item(current_row, 3).text()
        cliente_nombre = self.ui.presupuestos_tabla_presupuestos.item(current_row, 4).text()
        subtotal = float(self.ui.presupuestos_tabla_presupuestos.item(current_row, 5).text())
        total = float(self.ui.presupuestos_tabla_presupuestos.item(current_row, 6).text())

        # Convertir el nombre del cliente a su ID
        conn = self.connect_db()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT ID FROM CLIENTES WHERE NOMBRE = ?", (cliente_nombre,))
            cliente_row = cursor.fetchone()
            if not cliente_row:
                QMessageBox.warning(self, "Error", f"No se encontró un cliente con el nombre '{cliente_nombre}'.")
                return
            cliente_id = cliente_row[0]

            # Confirmar actualización
            confirm = QMessageBox.question(
                self, "Confirmar Edición", f"¿Guardar cambios en el presupuesto con ID {id_presupuesto}?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )
            if confirm == QMessageBox.Yes:
                # Actualizar el presupuesto
                cursor.execute('''
                    UPDATE PRESUPUESTOS
                    SET NOMBRE = ?, FECHA_CREACION = ?, FECHA_EXPIRACION = ?, CLIENTE = ?, SUBTOTAL = ?, TOTAL = ?
                    WHERE ID = ?
                ''', (nombre, fecha_creacion, fecha_expiracion, cliente_id, subtotal, total, id_presupuesto))
                conn.commit()
                QMessageBox.information(self, "Éxito", "Presupuesto actualizado correctamente.")
                self.cargar_presupuestos()# Recargar la tabla
                # Cargar presupuestos en el combo box de oportunidades
                self.cargar_presupuestos_combo_oportunidades()
        except sqlite3.Error as e:
            QMessageBox.warning(self, "Error", f"No se pudo actualizar el presupuesto: {e}")
        finally:
            conn.close()

    # OPORTUNIDADES
    def configurar_formulario_nueva_oportunidad(self):
        """Configura la página para crear una nueva oportunidad."""
        # Configurar la fecha predeterminada como el día actual
        self.ui.nueva_oportunidad_fecha.setDate(QtCore.QDate.currentDate())
        self.ui.nueva_oportunidad_fecha.setCalendarPopup(True)  # Habilitar el calendario desplegable

        # Configurar el estado predeterminado
        self.ui.nueva_oportunidad_estado.setText("Nuevo")  # Estado inicial

        # Cargar clientes en el combo box
        self.cargar_clientes_combo_oportunidades()

        # Cargar presupuestos en el combo box
        self.cargar_presupuestos_combo_oportunidades()

    def cargar_clientes_combo_oportunidades(self):
        """Carga los clientes en el combo box del formulario de nueva oportunidad."""
        conn = self.connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT ID, NOMBRE FROM CLIENTES")
        clientes = cursor.fetchall()
        conn.close()

        self.ui.nueva_oportunidad_cBox_Cliente.clear()
        for cliente in clientes:
            self.ui.nueva_oportunidad_cBox_Cliente.addItem(cliente[1], cliente[0])  # Mostrar nombre, almacenar ID

    def cargar_presupuestos_combo_oportunidades(self):
        """Carga los presupuestos en el combo box del formulario de nueva oportunidad."""
        conn = self.connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT ID, NOMBRE FROM PRESUPUESTOS")
        presupuestos = cursor.fetchall()
        conn.close()

        self.ui.nueva_oportunidad_cbox_presupuesto.clear()
        for presupuesto in presupuestos:
            self.ui.nueva_oportunidad_cbox_presupuesto.addItem(presupuesto[1], presupuesto[0])  # Mostrar nombre, almacenar ID


    def crear_nueva_oportunidad(self):
        """Valida y guarda una nueva oportunidad en la base de datos."""
        nombre = self.ui.nueva_oportunidad_nombre_oportunidad.text()
        cliente_id = self.ui.nueva_oportunidad_cBox_Cliente.currentData()
        presupuesto_id = self.ui.nueva_oportunidad_cbox_presupuesto.currentData()
        fecha = self.ui.nueva_oportunidad_fecha.date().toString("yyyy-MM-dd")
        ingreso_esperado = self.ui.nueva_oportunidad_ingreso_esperado.text()
        estado = self.ui.nueva_oportunidad_estado.text()

        # Validar campos
        if not nombre or not cliente_id or not presupuesto_id or not ingreso_esperado:
            QMessageBox.warning(self, "Error", "Por favor, completa todos los campos.")
            return

        if not ingreso_esperado.replace('.', '', 1).isdigit() or float(ingreso_esperado) < 0:
            QMessageBox.warning(self, "Error", "El ingreso esperado debe ser un número positivo.")
            return

        # Insertar en la base de datos
        conn = self.connect_db()
        try:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO OPORTUNIDADES (NOMBRE_OPORTUNIDAD, CLIENTE, PRESUPUESTO, FECHA, INGRESO_ESPERADO, ESTADO)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (nombre, cliente_id, presupuesto_id, fecha, float(ingreso_esperado), estado))
            conn.commit()
            QMessageBox.information(self, "Éxito", "Oportunidad creada correctamente.")
            self.limpiar_formulario_nueva_oportunidad()  # Limpiar formulario después de guardar
            self.cargar_oportunidades()  # Refrescar la tabla de oportunidades
            self.cargar_pipeline() #Actualizar Pipeline
        except sqlite3.Error as e:
            QMessageBox.warning(self, "Error", f"No se pudo guardar la oportunidad: {e}")
        finally:
            conn.close()

    def limpiar_formulario_nueva_oportunidad(self):
        """Limpia los campos del formulario de nueva oportunidad."""
        self.ui.nueva_oportunidad_nombre_oportunidad.clear()
        self.ui.nueva_oportunidad_cBox_Cliente.setCurrentIndex(-1)  # Limpiar selección de cliente
        self.ui.nueva_oportunidad_cbox_presupuesto.setCurrentIndex(-1)  # Limpiar selección de presupuesto
        self.ui.nueva_oportunidad_ingreso_esperado.clear()
        self.ui.nueva_oportunidad_estado.setText("Nuevo")  # Reiniciar estado
        self.ui.nueva_oportunidad_fecha.setDate(QtCore.QDate.currentDate())

    def cargar_oportunidades(self):
        """Carga las oportunidades desde la base de datos y las muestra en la tabla."""
        conn = self.connect_db()
        cursor = conn.cursor()

        # Consulta ordenada por estado y fecha descendente
        cursor.execute('''
            SELECT 
                o.ID, 
                o.NOMBRE_OPORTUNIDAD, 
                c.NOMBRE AS CLIENTE, 
                o.FECHA, 
                p.NOMBRE AS PRESUPUESTO, 
                o.INGRESO_ESPERADO, 
                o.ESTADO
            FROM OPORTUNIDADES o
            JOIN CLIENTES c ON o.CLIENTE = c.ID
            JOIN PRESUPUESTOS p ON o.PRESUPUESTO = p.ID
            ORDER BY o.ESTADO, o.FECHA DESC
        ''')
        oportunidades = cursor.fetchall()
        conn.close()

        # Limpiar la tabla antes de cargar datos
        self.ui.oportunidades_tabla.setRowCount(0)

        # Llenar la tabla con los datos obtenidos
        for row_num, oportunidad in enumerate(oportunidades):
            self.ui.oportunidades_tabla.insertRow(row_num)
            for col_num, data in enumerate(oportunidad):
                item = QtWidgets.QTableWidgetItem(str(data))
                # Hacer campos específicos no editables
                if col_num in [0, 2, 4, 6]:  # ID, Cliente, Presupuesto y Estado
                    item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEditable)
                self.ui.oportunidades_tabla.setItem(row_num, col_num, item)


    def editar_oportunidad(self):
        """Edita la oportunidad seleccionada en la tabla."""
        current_row = self.ui.oportunidades_tabla.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Error", "Por favor, selecciona una oportunidad.")
            return

        # Obtener el ID de la oportunidad seleccionada
        id_oportunidad = int(self.ui.oportunidades_tabla.item(current_row, 0).text())

        # Obtener los valores editables de la tabla
        nombre_oportunidad = self.ui.oportunidades_tabla.item(current_row, 1).text()
        fecha = self.ui.oportunidades_tabla.item(current_row, 3).text()
        ingreso_esperado = self.ui.oportunidades_tabla.item(current_row, 5).text()

        # Validar el formato de la fecha
        if not QtCore.QDate.fromString(fecha, "yyyy-MM-dd").isValid():
            QMessageBox.warning(self, "Error", "La fecha debe estar en formato yyyy-MM-dd.")
            return

        # Validar ingreso esperado
        if not ingreso_esperado.replace('.', '', 1).isdigit() or float(ingreso_esperado) < 0:
            QMessageBox.warning(self, "Error", "El ingreso esperado debe ser un número positivo.")
            return

        # Confirmar actualización
        confirm = QMessageBox.question(
            self, "Confirmar Edición", f"¿Guardar cambios en la oportunidad con ID {id_oportunidad}?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            conn = self.connect_db()
            try:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE OPORTUNIDADES
                    SET NOMBRE_OPORTUNIDAD = ?, FECHA = ?, INGRESO_ESPERADO = ?
                    WHERE ID = ?
                ''', (nombre_oportunidad, fecha, float(ingreso_esperado), id_oportunidad))
                conn.commit()
                QMessageBox.information(self, "Éxito", "Oportunidad actualizada correctamente.")
                self.cargar_oportunidades()  # Refrescar la tabla de oportunidades
                self.cargar_pipeline() #Actualizar Pipeline
            except sqlite3.Error as e:
                QMessageBox.warning(self, "Error", f"No se pudo actualizar la oportunidad: {e}")
            finally:
                conn.close()


    def eliminar_oportunidad(self):
        """Elimina la oportunidad seleccionada en la tabla."""
        current_row = self.ui.oportunidades_tabla.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Error", "Por favor, selecciona una oportunidad.")
            return

        # Obtener el ID de la oportunidad seleccionada
        id_oportunidad = int(self.ui.oportunidades_tabla.item(current_row, 0).text())

        # Confirmar eliminación
        confirm = QMessageBox(self)
        confirm.setWindowTitle("Confirmar Eliminación")
        confirm.setText(f"¿Estás seguro de eliminar la oportunidad con ID {id_oportunidad}?")
        confirm.setIcon(QMessageBox.Question)

        btn_si = confirm.addButton("Sí", QMessageBox.YesRole)
        btn_no = confirm.addButton("No", QMessageBox.NoRole)

        confirm.exec_()

        if confirm.clickedButton() == btn_si:
            conn = self.connect_db()
            try:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM OPORTUNIDADES WHERE ID = ?", (id_oportunidad,))
                conn.commit()
                QMessageBox.information(self, "Éxito", "Oportunidad eliminada correctamente.")
                self.cargar_oportunidades()  # Refrescar la tabla
                self.cargar_pipeline() #Actualizar Pipeline
            except sqlite3.Error as e:
                QMessageBox.warning(self, "Error", f"No se pudo eliminar la oportunidad: {e}")
            finally:
                conn.close()

    # Métodos para el Pipeline

    def cargar_pipeline(self):
        """Carga las oportunidades en las listas del pipeline según su estado, ordenadas por fecha."""
        conn = self.connect_db()
        cursor = conn.cursor()

        # Consulta las oportunidades ordenadas por fecha descendente
        cursor.execute('''
            SELECT 
                o.ID, 
                o.NOMBRE_OPORTUNIDAD, 
                o.FECHA, 
                c.NOMBRE AS CLIENTE, 
                p.NOMBRE AS PRESUPUESTO, 
                o.INGRESO_ESPERADO, 
                o.ESTADO
            FROM OPORTUNIDADES o
            JOIN CLIENTES c ON o.CLIENTE = c.ID
            JOIN PRESUPUESTOS p ON o.PRESUPUESTO = p.ID
            ORDER BY o.FECHA DESC
        ''')
        oportunidades = cursor.fetchall()
        conn.close()

        # Limpiar las listas
        self.ui.list_nuevo.clear()
        self.ui.list_calificado.clear()
        self.ui.list_propuesta.clear()
        self.ui.list_ganado.clear()

        # Organizar las oportunidades en las listas correspondientes
        for oportunidad in oportunidades:
            id_op, nombre, fecha, cliente, presupuesto, ingreso, estado = oportunidad
            item = QtWidgets.QListWidgetItem(f"{nombre} - {fecha}")
            item.setData(QtCore.Qt.UserRole, id_op)  # Asociar solo el ID de la oportunidad con el ítem
            item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEditable)  # Hacer los ítems no editables

            if estado == "Nuevo":
                self.ui.list_nuevo.addItem(item)
            elif estado == "Calificado":
                self.ui.list_calificado.addItem(item)
            elif estado == "Propuesta":
                self.ui.list_propuesta.addItem(item)
            elif estado == "Ganado":
                self.ui.list_ganado.addItem(item)

        # Conectar eventos de clic para mostrar detalles
        self.ui.list_nuevo.itemClicked.connect(self.mostrar_detalle_oportunidad)
        self.ui.list_calificado.itemClicked.connect(self.mostrar_detalle_oportunidad)
        self.ui.list_propuesta.itemClicked.connect(self.mostrar_detalle_oportunidad)
        self.ui.list_ganado.itemClicked.connect(self.mostrar_detalle_oportunidad)

    def mostrar_detalle_oportunidad(self, item):
        """Muestra los detalles de la oportunidad seleccionada en el QTextEdit."""
        oportunidad_id = item.data(QtCore.Qt.UserRole)

        # Obtener los detalles de la base de datos
        conn = self.connect_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT 
                o.NOMBRE_OPORTUNIDAD, 
                o.FECHA, 
                c.NOMBRE AS CLIENTE, 
                p.NOMBRE AS PRESUPUESTO, 
                o.INGRESO_ESPERADO, 
                o.ESTADO
            FROM OPORTUNIDADES o
            JOIN CLIENTES c ON o.CLIENTE = c.ID
            JOIN PRESUPUESTOS p ON o.PRESUPUESTO = p.ID
            WHERE o.ID = ?
        ''', (oportunidad_id,))
        detalle = cursor.fetchone()
        conn.close()

        if detalle:
            nombre, fecha, cliente, presupuesto, ingreso, estado = detalle
            descripcion = (
                f"Nombre: {nombre}. "
                f"Fecha: {fecha}. "
                f"Cliente: {cliente}. "
                f"Presupuesto: {presupuesto}. "
                f"Ingreso Esperado: {ingreso} €."
                #f"Estado: {estado}"
            )
            self.ui.detalle_oportunidad.setText(descripcion)



    def mover_fase_siguiente(self):
        """Mueve la oportunidad seleccionada a la siguiente fase."""
        # Determinar de cuál lista se está moviendo
        for lista, siguiente_estado in [
            (self.ui.list_nuevo, "Calificado"),
            (self.ui.list_calificado, "Propuesta"),
            (self.ui.list_propuesta, "Ganado"),
        ]:
            if lista.currentItem():
                oportunidad_id = lista.currentItem().data(QtCore.Qt.UserRole)
                break
        else:
            QMessageBox.warning(self, "Error", "Por favor, selecciona una oportunidad para mover.")
            return

        # Actualizar el estado en la base de datos
        conn = self.connect_db()
        try:
            cursor = conn.cursor()
            cursor.execute("UPDATE OPORTUNIDADES SET ESTADO = ? WHERE ID = ?", (siguiente_estado, oportunidad_id))
            conn.commit()
            self.cargar_pipeline()  # Recargar las listas
            self.cargar_oportunidades()  # Refrescar la tabla de oportunidades
            QMessageBox.information(self, "Éxito", "La oportunidad se ha movido a la siguiente fase.")
        except sqlite3.Error as e:
            QMessageBox.warning(self, "Error", f"No se pudo mover la oportunidad: {e}")
            #QMessageBox.warning(self, "Error", f"No se pudo mover la oportunidad: Estado 'Ganado' es la última posición.")
        finally:
            conn.close()

    def mover_fase_anterior(self):
        """Mueve la oportunidad seleccionada a la fase anterior."""
        # Determinar de cuál lista se está moviendo
        for lista, anterior_estado in [
            (self.ui.list_calificado, "Nuevo"),
            (self.ui.list_propuesta, "Calificado"),
            (self.ui.list_ganado, "Propuesta"),
        ]:
            if lista.currentItem():
                oportunidad_id = lista.currentItem().data(QtCore.Qt.UserRole)
                break
        else:
            QMessageBox.warning(self, "Error", "Por favor, selecciona una oportunidad para mover.")
            return

        # Actualizar el estado en la base de datos
        conn = self.connect_db()
        try:
            cursor = conn.cursor()
            cursor.execute("UPDATE OPORTUNIDADES SET ESTADO = ? WHERE ID = ?", (anterior_estado, oportunidad_id))
            conn.commit()
            self.cargar_pipeline()  # Recargar las listas
            self.cargar_oportunidades()  # Refrescar la tabla de oportunidades
            QMessageBox.information(self, "Éxito", "La oportunidad se ha movido a la fase anterior.")
        except sqlite3.Error as e:
            QMessageBox.warning(self, "Error", f"No se pudo mover la oportunidad: {e}")
            #QMessageBox.warning(self, "Error", f"No se pudo mover la oportunidad: Estado 'Ganado' es la última posición.")
        finally:
            conn.close()

    # Establecer el logo del CRM
    def configurar_logo(self):
        """Configura el logo en el QLabel."""
        ruta_logo = "icons/logo.png"  # Ruta de la imagen
        pixmap = QPixmap(ruta_logo)  # Cargar la imagen
        if not pixmap.isNull():
            self.ui.logo_label.setPixmap(pixmap)  # Asignar la imagen al QLabel
            self.ui.logo_label.setScaledContents(True)  # Escalar el contenido si es necesario
        else:
            print("No se pudo cargar la imagen del logo. Verifica la ruta.")


    def cerrar_sesion(self):
        """Cierra sesión y regresa a la ventana de inicio de sesión."""
        # Crear un QMessageBox personalizado
        confirm = QMessageBox(self)
        confirm.setIcon(QMessageBox.Question)
        confirm.setWindowTitle("Confirmar Cierre de Sesión")
        confirm.setText("¿Estás seguro/a de que deseas cerrar sesión?")
        
        # Agregar botones personalizados
        btn_si = confirm.addButton("Sí", QMessageBox.YesRole)
        btn_no = confirm.addButton("No", QMessageBox.NoRole)
        
        confirm.setDefaultButton(btn_no)  # Botón predeterminado
        confirm.exec_()

        # Verificar la opción seleccionada
        if confirm.clickedButton() == btn_si:
            self.close()  # Cerrar la ventana principal
            self.login_window = LoginWindow()  # Crear una nueva instancia de la ventana de inicio de sesión
            self.login_window.show()  # Mostrar la ventana de inicio de sesión

class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Conectar botones
        self.ui.btn_login.clicked.connect(self.login)
        self.ui.btn_register.clicked.connect(self.register)
        # Configurar el logo
        self.configurar_logo()

    def login(self):
        company_name = self.ui.txt_company.text()
        email = self.ui.txt_email.text()
        password = self.ui.txt_password.text()

        if not company_name or not email or not password:
            QMessageBox.warning(self, "Error", "Por favor, completa todos los campos.")
            return

        db_path = f"database/{company_name}.db"
        if not os.path.exists(db_path):
            QMessageBox.warning(self, "Error", "La empresa no está registrada.")
            return

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM IDENTIFICACION
            WHERE NOMBRE_EMPRESA = ? AND MAIL = ? AND PASSWORD = ?
        ''', (company_name, email, password))
        result = cursor.fetchone()
        conn.close()

        if result:
            QMessageBox.information(self, "Éxito", "Inicio de sesión exitoso.")
            self.open_main_window(company_name)
        else:
            QMessageBox.warning(self, "Error", "Credenciales incorrectas.")

    def register(self):
        company_name = self.ui.txt_company.text()
        email = self.ui.txt_email.text()
        password = self.ui.txt_password.text()
        password_2 = self.ui.txt_password_2.text()  # Obtener el texto del campo de repetición

        # Validar campos vacíos
        if not company_name or not email or not password or not password_2:
            QMessageBox.warning(self, "Error", "Por favor, completa todos los campos.")
            return

        # Verificar que las contraseñas coincidan
        if password != password_2:
            QMessageBox.warning(self, "Error", "Las contraseñas no coinciden. Por favor, inténtalo de nuevo.")
            return

        # Crear base de datos y registrar empresa
        if create_database(company_name):
            insert_company(company_name, password, email)
            QMessageBox.information(self, "Éxito", "Empresa registrada correctamente.")
            self.open_main_window(company_name)
        else:
            QMessageBox.warning(self, "Error", "La empresa ya existe.")

    
    def open_main_window(self, company_name):
        """Abre la ventana principal y carga los datos de la empresa."""
        conn = sqlite3.connect(f"database/{company_name}.db")
        cursor = conn.cursor()
        cursor.execute('SELECT NOMBRE_EMPRESA, MAIL, DIRECCION, TELEFONO FROM IDENTIFICACION WHERE NOMBRE_EMPRESA = ?', (company_name,))
        empresa_data = cursor.fetchone()
        conn.close()

        if empresa_data:
            # Abre la ventana principal y pasa los datos de la empresa
            self.main_window = MainWindow(company_name, empresa_data)
            self.main_window.show()
            self.close()

    def configurar_logo(self):
        """Configura el logo en el QLabel."""
        ruta_logo = "icons/logo.png"  # Ruta de la imagen
        pixmap = QPixmap(ruta_logo)  # Cargar la imagen
        if not pixmap.isNull():
            self.ui.logo_label.setPixmap(pixmap)  # Asignar la imagen al QLabel
            self.ui.logo_label.setScaledContents(True)  # Escalar el contenido si es necesario
        else:
            print("No se pudo cargar la imagen del logo. Verifica la ruta.")


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec_())
