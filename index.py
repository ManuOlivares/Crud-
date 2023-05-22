from tkinter import ttk
from tkinter import *

import sqlite3


class Product:
    db_name = 'db_market.db'

    def __init__(self, window):
        self.wind = window
        self.wind.title('Products Application')

        # Crear el Frame Contenedor
        frame = LabelFrame(self.wind, text='Registrar nuevo producto')
        frame.grid(row=0, column=0, columnspan=3, pady=20)

        # Input de Búsqueda
        Label(frame, text='Buscar: ').grid(row=0, column=0)
        self.search_entry = Entry(frame)
        self.search_entry.grid(row=0, column=1)

        # Botón de Búsqueda
        ttk.Button(frame, text='Buscar', command=self.search_product).grid(row=0, column=3)

        # Input de Nombre
        Label(frame, text='Nombre: ').grid(row=1, column=0)
        self.name = Entry(frame)
        self.name.focus()
        self.name.grid(row=1, column=1)

        # Input de Precio
        Label(frame, text='Precio: ').grid(row=2, column=0)
        self.price = Entry(frame)
        self.price.grid(row=2, column=1)

        # Botón para Agregar Producto
        ttk.Button(frame, text='Guardar', command=self.save_product).grid(row=3, columnspan=2, sticky=W + E)

        # Mensaje de Salida
        self.message = Label(text='', fg='red')
        self.message.grid(row=3, column=0, columnspan=2, sticky=W + E)

        # Crear el Treeview
        self.tree = ttk.Treeview(height=10, columns=2)
        self.tree.grid(row=4, column=0, columnspan=2, sticky=NSEW)

        # Configurar las cabeceras del Treeview
        self.tree.heading('#0', text='Nombre', anchor=CENTER)
        self.tree.heading('#1', text='Precio', anchor=CENTER)

        # Configurar el Scrollbar
        scrollbar = ttk.Scrollbar(self.wind, orient=VERTICAL, command=self.tree.yview)
        scrollbar.grid(row=4, column=2, sticky=NSEW)

        self.tree.configure(yscrollcommand=scrollbar.set)

        # Botones
        ttk.Button(text='Editar', command=self.edit_product).grid(row=5, column=0, sticky=W + E)
        ttk.Button(text='Eliminar', command=self.delete_product).grid(row=5, column=1, sticky=W + E)
        ttk.Button(frame, text='Actualizar', command=self.refresh_products).grid(row=6, columnspan=2, sticky=W + E)

        # Atributo Adicional
        self.editing_product = False

        # Llenar la Tabla
        self.get_products()

    def run_query(self, query, parameters=()):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            result = cursor.execute(query, parameters)
            conn.commit()
        return result

    def get_products(self):
        # Limpiar la tabla
        self.tree.delete(*self.tree.get_children())

        # Consulta
        query = 'SELECT * FROM producto ORDER BY nombre DESC'
        db_rows = self.run_query(query)

        # Llenar los datos
        for row in db_rows:
            self.tree.insert('', 0, text=row[1], values=row[2])

    def validation(self):
        return len(self.name.get()) != 0 and len(self.price.get()) != 0

    def add_product(self):
        if self.validation():
            query = 'INSERT INTO producto VALUES(null, ?, ?)'
            parameters = (self.name.get(), self.price.get())
            self.run_query(query, parameters)
            self.message['text'] = 'Producto {} agregado correctamente'.format(self.name.get())
            self.clear_fields()
            self.get_products()
        else:
            self.message['text'] = 'Nombre del producto y precio son requeridos'

    def update_product(self):
        if self.validation():
            name = self.tree.item(self.tree.selection())['text']
            new_name = self.name.get()
            new_price = self.price.get()

            query = 'UPDATE producto SET nombre = ?, precio = ? WHERE nombre = ?'
            parameters = (new_name, new_price, name)
            self.run_query(query, parameters)
            self.message['text'] = 'Producto {} actualizado correctamente'.format(name)
            self.clear_fields()
            self.get_products()
        else:
            self.message['text'] = 'Nombre del producto y precio son requeridos'

    def save_product(self):
        if self.editing_product:
            self.update_product()
        else:
            self.add_product()

    def clear_fields(self):
        self.name.delete(0, END)
        self.price.delete(0, END)
        self.name.insert(0, '')
        self.price.insert(0, '')
        self.editing_product = False

    def delete_product(self):
        self.message['text'] = ''
        try:
            self.tree.item(self.tree.selection())['text']
        except IndexError as e:
            self.message['text'] = 'Selecciona un producto'
            return
        name = self.tree.item(self.tree.selection())['text']
        query = 'DELETE FROM producto WHERE nombre = ?'
        self.run_query(query, (name,))
        self.message['text'] = 'Producto {} eliminado correctamente'.format(name)
        self.get_products()

    def edit_product(self):
        self.message['text'] = ''
        try:
            self.tree.item(self.tree.selection())['text'][0]
        except IndexError as e:
            self.message['text'] = 'Selecciona un producto'
            return
        name = self.tree.item(self.tree.selection())['text']
        old_price = self.tree.item(self.tree.selection())['values'][0]

        # Limpiar los campos de entrada
        self.clear_fields()

        # Rellenar los campos de entrada con los datos existentes
        self.name.insert(0, name)
        self.price.insert(0, old_price)

        # Establecer editing_product en True
        self.editing_product = True

    def refresh_products(self):
        self.get_products()

    def search_product(self):
        search_term = self.search_entry.get()
        query = "SELECT * FROM producto WHERE nombre LIKE ?"
        parameters = ('%' + search_term + '%',)
        db_rows = self.run_query(query, parameters)

        # Limpiar la tabla
        self.tree.delete(*self.tree.get_children())

        # Llenar la tabla con los resultados de búsqueda
        for row in db_rows:
            self.tree.insert('', 0, text=row[1], values=row[2])


if __name__ == '__main__':
    window = Tk()
    application = Product(window)
    window.mainloop()
