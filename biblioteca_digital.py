import datetime

class Libro:
    def __init__(self, titulo, autor, isbn, cantidad):
        if not titulo or not isinstance(titulo, str):
            raise ValueError("El título del libro no puede estar vacío y debe ser una cadena de texto.")
        if not autor or not isinstance(autor, str):
            raise ValueError("El autor del libro no puede estar vacío y debe ser una cadena de texto.")
        if not isbn or not isinstance(isbn, str):
            raise ValueError("El ISBN del libro no puede estar vacío y debe ser una cadena de texto.")
        if not isinstance(cantidad, int) or cantidad < 0:
            raise ValueError("La cantidad de libros debe ser un número entero no negativo.")

        self.titulo = titulo
        self.autor = autor
        self.isbn = isbn
        self.cantidad = cantidad

    def __str__(self):
        return f"{self.titulo} por {self.autor} (ISBN: {self.isbn})"

    def disponible(self):
        return self.cantidad > 0

    def prestar(self):
        if self.disponible():
            self.cantidad -= 1
            return True
        return False

    def devolver(self):
        self.cantidad += 1

class Usuario:
    def __init__(self, nombre, id_usuario):
        if not nombre or not isinstance(nombre, str):
            raise ValueError("El nombre del usuario no puede estar vacío y debe ser una cadena de texto.")
        if not id_usuario or not isinstance(id_usuario, str):
            raise ValueError("El ID del usuario no puede estar vacío y debe ser una cadena de texto.")

        self.nombre = nombre
        self.id_usuario = id_usuario
        self.libros_prestados = []

    def __str__(self):
        return f"{self.nombre} (ID: {self.id_usuario})"

    def agregar_libro_prestado(self, libro):
        if isinstance(libro, Libro):
            self.libros_prestados.append(libro)
        else:
            raise ValueError("Se debe agregar un objeto de tipo Libro.")

    def remover_libro_prestado(self, libro):
        if isinstance(libro, Libro) and libro in self.libros_prestados:
            self.libros_prestados.remove(libro)
            return True
        return False

class Prestamo:
    def __init__(self, libro, usuario, fecha_prestamo):
        if not isinstance(libro, Libro):
            raise ValueError("El objeto libro debe ser de la clase Libro.")
        if not isinstance(usuario, Usuario):
            raise ValueError("El objeto usuario debe ser de la clase Usuario.")
        if not isinstance(fecha_prestamo, datetime.date):
             raise ValueError("La fecha de préstamo debe ser un objeto datetime.date.")

        self.libro = libro
        self.usuario = usuario
        self.fecha_prestamo = fecha_prestamo
        self.fecha_devolucion = None

    def __str__(self):
        return f"Préstamo de '{self.libro.titulo}' a '{self.usuario.nombre}' el {self.fecha_prestamo}"

    def calcular_multa(self, fecha_actual, dias_permitidos=14, costo_por_dia=0.5):
        if not isinstance(fecha_actual, datetime.date):
            raise ValueError("La fecha actual debe ser un objeto datetime.date.")

        if self.fecha_devolucion is None:
            dias_prestamo = (fecha_actual - self.fecha_prestamo).days
            if dias_prestamo > dias_permitidos:
                dias_retraso = dias_prestamo - dias_permitidos
                return dias_retraso * costo_por_dia
        return 0

    def registrar_devolucion(self, fecha_devolucion):
        if not isinstance(fecha_devolucion, datetime.date):
             raise ValueError("La fecha de devolución debe ser un objeto datetime.date.")
        if fecha_devolucion < self.fecha_prestamo:
            raise ValueError("La fecha de devolución no puede ser anterior a la fecha de préstamo.")

        self.fecha_devolucion = fecha_devolucion

import json
from datetime import date
from collections import defaultdict

class Biblioteca:
    def __init__(self):
        self.libros = {}
        self.usuarios = {}
        self.prestamos = []

    def cargar_datos_iniciales(self, archivo):
        try:
            with open(archivo, 'r') as f:
                data = json.load(f)
                for libro_data in data.get('libros', []):
                    try:
                        libro = Libro(libro_data['titulo'], libro_data['autor'], libro_data['isbn'], libro_data['cantidad'])
                        self.libros[libro.isbn] = libro
                    except (ValueError, KeyError) as e:
                        print(f"Error al cargar libro: {e} en datos: {libro_data}")
                for usuario_data in data.get('usuarios', []):
                    try:
                        usuario = Usuario(usuario_data['nombre'], usuario_data['id_usuario'])
                        if usuario.id_usuario in self.usuarios:
                             print(f"Advertencia: Usuario con ID {usuario.id_usuario} duplicado, saltando.")
                             continue
                        self.usuarios[usuario.id_usuario] = usuario
                    except (ValueError, KeyError) as e:
                        print(f"Error al cargar usuario: {e} en datos: {usuario_data}")
        except FileNotFoundError:
            print(f"Error: Archivo no encontrado en {archivo}")
        except json.JSONDecodeError:
            print(f"Error: No se pudo decodificar el archivo JSON en {archivo}")
        except Exception as e:
            print(f"Error inesperado al cargar datos: {e}")

    def buscar_libro(self, criterio, valor):
        resultados = []
        criterio = criterio.lower()
        for libro in self.libros.values():
            if criterio == 'titulo' and valor.lower() in libro.titulo.lower():
                resultados.append(libro)
            elif criterio == 'autor' and valor.lower() in libro.autor.lower():
                resultados.append(libro)
            elif criterio == 'isbn' and valor.lower() == libro.isbn.lower():
                resultados.append(libro)
        return resultados

    def registrar_usuario(self, nombre, id_usuario):
        if id_usuario in self.usuarios:
            print(f"Error: El usuario con ID {id_usuario} ya existe.")
            return None
        try:
            usuario = Usuario(nombre, id_usuario)
            self.usuarios[id_usuario] = usuario
            return usuario
        except ValueError as e:
            print(f"Error al registrar usuario: {e}")
            return None

    def registrar_prestamo(self, libro_isbn, usuario_id, fecha_prestamo_str):
        if libro_isbn not in self.libros:
            print(f"Error: Libro con ISBN {libro_isbn} no encontrado.")
            return None
        if usuario_id not in self.usuarios:
            print(f"Error: Usuario con ID {usuario_id} no encontrado.")
            return None

        libro = self.libros[libro_isbn]
        usuario = self.usuarios[usuario_id]

        if not libro.disponible():
            print(f"Error: El libro '{libro.titulo}' no está disponible.")
            return None

        try:
            fecha_prestamo = datetime.datetime.strptime(fecha_prestamo_str, '%Y-%m-%d').date()
            prestamo = Prestamo(libro, usuario, fecha_prestamo)
            self.prestamos.append(prestamo)
            libro.prestar()
            usuario.agregar_libro_prestado(libro)
            print(f"Préstamo registrado: '{libro.titulo}' a '{usuario.nombre}'.")
            return prestamo
        except ValueError as e:
            print(f"Error en el formato de la fecha de préstamo: {e}")
            return None


    def registrar_devolucion(self, libro_isbn, usuario_id, fecha_devolucion_str):
        for prestamo in self.prestamos:
            if prestamo.libro.isbn == libro_isbn and prestamo.usuario.id_usuario == usuario_id and prestamo.fecha_devolucion is None:
                try:
                    fecha_devolucion = datetime.datetime.strptime(fecha_devolucion_str, '%Y-%m-%d').date()
                    multa = prestamo.calcular_multa(fecha_devolucion)
                    prestamo.registrar_devolucion(fecha_devolucion)
                    prestamo.libro.devolver()
                    prestamo.usuario.remover_libro_prestado(prestamo.libro)
                    print(f"Devolución registrada para '{prestamo.libro.titulo}'. Multa: {multa:.2f} euros.")
                    return multa
                except ValueError as e:
                    print(f"Error en el formato de la fecha de devolución: {e}")
                    return None
                except Exception as e:
                    print(f"Error al registrar devolución: {e}")
                    return None

        print(f"Error: No se encontró un préstamo activo para el libro con ISBN {libro_isbn} y usuario con ID {usuario_id}.")
        return None

    def calcular_estadisticas(self):
        total_libros = len(self.libros)
        libros_disponibles = sum(libro.cantidad for libro in self.libros.values())
        total_usuarios = len(self.usuarios)
        prestamos_activos = sum(1 for prestamo in self.prestamos if prestamo.fecha_devolucion is None)
        total_multas = sum(prestamo.calcular_multa(date.today()) for prestamo in self.prestamos if prestamo.fecha_devolucion is None)

        return {
            "total_libros": total_libros,
            "libros_disponibles": libros_disponibles,
            "total_usuarios": total_usuarios,
            "prestamos_activos": prestamos_activos,
            "total_multas_pendientes": total_multas
        }

    def generar_reporte_mensual(self, mes, anio):
        reporte = f"Reporte Mensual de la Biblioteca - {mes}/{anio}\n"
        reporte += "=" * 40 + "\n\n"

        prestamos_mes = [
            p for p in self.prestamos
            if p.fecha_prestamo.month == mes and p.fecha_prestamo.year == anio
        ]

        if prestamos_mes:
            reporte += "Detalle de Préstamos del Mes:\n"
            for prestamo in prestamos_mes:
                estado = "Activo" if prestamo.fecha_devolucion is None else f"Devuelto el {prestamo.fecha_devolucion}"
                multa = prestamo.calcular_multa(date.today() if prestamo.fecha_devolucion is None else prestamo.fecha_devolucion)
                reporte += f"- Libro: '{prestamo.libro.titulo}' (ISBN: {prestamo.libro.isbn})\n"
                reporte += f"  Usuario: '{prestamo.usuario.nombre}' (ID: {prestamo.usuario.id_usuario})\n"
                reporte += f"  Fecha Préstamo: {prestamo.fecha_prestamo}\n"
                reporte += f"  Estado: {estado}\n"
                reporte += f"  Multa calculada: {multa:.2f} euros\n"
                reporte += "-----\n"
        else:
            reporte += "No hubo préstamos registrados en este mes.\n"

        reporte += "\n" + "=" * 40 + "\n"
        reporte += "Estadísticas Generales:\n"
        estadisticas = self.calcular_estadisticas()
        for key, value in estadisticas.items():
            reporte += f"- {key.replace('_', ' ').title()}: {value}\n"

        return reporte

import json
import datetime

# Re-defining classes to ensure they are available in the current scope for instantiation in the same block
class Libro:
    def __init__(self, titulo, autor, isbn, cantidad):
        if not titulo or not isinstance(titulo, str):
            raise ValueError("El título del libro no puede estar vacío y debe ser una cadena de texto.")
        if not autor or not isinstance(autor, str):
            raise ValueError("El autor del libro no puede estar vacío y debe ser una cadena de texto.")
        if not isbn or not isinstance(isbn, str):
            raise ValueError("El ISBN del libro no puede estar vacío y debe ser una cadena de texto.")
        if not isinstance(cantidad, int) or cantidad < 0:
            raise ValueError("La cantidad de libros debe ser un número entero no negativo.")

        self.titulo = titulo
        self.autor = autor
        self.isbn = isbn
        self.cantidad = cantidad

    def __str__(self):
        return f"{self.titulo} por {self.autor} (ISBN: {self.isbn})"

    def disponible(self):
        return self.cantidad > 0

    def prestar(self):
        if self.disponible():
            self.cantidad -= 1
            return True
        return False

    def devolver(self):
        self.cantidad += 1

class Usuario:
    def __init__(self, nombre, id_usuario):
        if not nombre or not isinstance(nombre, str):
            raise ValueError("El nombre del usuario no puede estar vacío y debe ser una cadena de texto.")
        if not id_usuario or not isinstance(id_usuario, str):
            raise ValueError("El ID del usuario no puede estar vacío y debe ser una cadena de texto.")

        self.nombre = nombre
        self.id_usuario = id_usuario
        self.libros_prestados = []

    def __str__(self):
        return f"{self.nombre} (ID: {self.id_usuario})"

    def agregar_libro_prestado(self, libro):
        if isinstance(libro, Libro):
            self.libros_prestados.append(libro)
        else:
            raise ValueError("Se debe agregar un objeto de tipo Libro.")

    def remover_libro_prestado(self, libro):
        if isinstance(libro, Libro) and libro in self.libros_prestados:
            self.libros_prestados.remove(libro)
            return True
        return False

class Prestamo:
    def __init__(self, libro, usuario, fecha_prestamo):
        if not isinstance(libro, Libro):
            raise ValueError("El objeto libro debe ser de la clase Libro.")
        if not isinstance(usuario, Usuario):
            raise ValueError("El objeto usuario debe ser de la clase Usuario.")
        if not isinstance(fecha_prestamo, datetime.date):
             raise ValueError("La fecha de préstamo debe ser un objeto datetime.date.")

        self.libro = libro
        self.usuario = usuario
        self.fecha_prestamo = fecha_prestamo
        self.fecha_devolucion = None

    def __str__(self):
        return f"Préstamo de '{self.libro.titulo}' a '{self.usuario.nombre}' el {self.fecha_prestamo}"

    def calcular_multa(self, fecha_actual, dias_permitidos=14, costo_por_dia=0.5):
        if not isinstance(fecha_actual, datetime.date):
            raise ValueError("La fecha actual debe ser un objeto datetime.date.")

        if self.fecha_devolucion is None:
            dias_prestamo = (fecha_actual - self.fecha_prestamo).days
            if dias_prestamo > dias_permitidos:
                dias_retraso = dias_prestamo - dias_permitidos
                return dias_retraso * costo_por_dia
        return 0

    def registrar_devolucion(self, fecha_devolucion):
        if not isinstance(fecha_devolucion, datetime.date):
             raise ValueError("La fecha de devolución debe ser un objeto datetime.date.")
        if fecha_devolucion < self.fecha_prestamo:
            raise ValueError("La fecha de devolución no puede ser anterior a la fecha de préstamo.")

        self.fecha_devolucion = fecha_devolucion


class Biblioteca:
    def __init__(self):
        self.libros = {}
        self.usuarios = {}
        self.prestamos = []

    def cargar_datos_iniciales(self, archivo):
        try:
            with open(archivo, 'r') as f:
                data = json.load(f)
                for libro_data in data.get('libros', []):
                    try:
                        libro = Libro(libro_data['titulo'], libro_data['autor'], libro_data['isbn'], libro_data['cantidad'])
                        self.libros[libro.isbn] = libro
                    except (ValueError, KeyError) as e:
                        print(f"Error al cargar libro: {e} en datos: {libro_data}")
                for usuario_data in data.get('usuarios', []):
                    try:
                        usuario = Usuario(usuario_data['nombre'], usuario_data['id_usuario'])
                        if usuario.id_usuario in self.usuarios:
                             print(f"Advertencia: Usuario con ID {usuario.id_usuario} duplicado, saltando.")
                             continue
                        self.usuarios[usuario.id_usuario] = usuario
                    except (ValueError, KeyError) as e:
                        print(f"Error al cargar usuario: {e} en datos: {usuario_data}")
        except FileNotFoundError:
            print(f"Error: Archivo no encontrado en {archivo}")
        except json.JSONDecodeError:
            print(f"Error: No se pudo decodificar el archivo JSON en {archivo}")
        except Exception as e:
            print(f"Error inesperado al cargar datos: {e}")

    def buscar_libro(self, criterio, valor):
        resultados = []
        criterio = criterio.lower()
        for libro in self.libros.values():
            if criterio == 'titulo' and valor.lower() in libro.titulo.lower():
                resultados.append(libro)
            elif criterio == 'autor' and valor.lower() in libro.autor.lower():
                resultados.append(libro)
            elif criterio == 'isbn' and valor.lower() == libro.isbn.lower():
                resultados.append(libro)
        return resultados

    def registrar_usuario(self, nombre, id_usuario):
        if id_usuario in self.usuarios:
            print(f"Error: El usuario con ID {id_usuario} ya existe.")
            return None
        try:
            usuario = Usuario(nombre, id_usuario)
            self.usuarios[id_usuario] = usuario
            return usuario
        except ValueError as e:
            print(f"Error al registrar usuario: {e}")
            return None

    def registrar_prestamo(self, libro_isbn, usuario_id, fecha_prestamo_str):
        if libro_isbn not in self.libros:
            print(f"Error: Libro con ISBN {libro_isbn} no encontrado.")
            return None
        if usuario_id not in self.usuarios:
            print(f"Error: Usuario con ID {usuario_id} no encontrado.")
            return None

        libro = self.libros[libro_isbn]
        usuario = self.usuarios[usuario_id]

        if not libro.disponible():
            print(f"Error: El libro '{libro.titulo}' no está disponible.")
            return None

        try:
            fecha_prestamo = datetime.datetime.strptime(fecha_prestamo_str, '%Y-%m-%d').date()
            prestamo = Prestamo(libro, usuario, fecha_prestamo)
            self.prestamos.append(prestamo)
            libro.prestar()
            usuario.agregar_libro_prestado(libro)
            print(f"Préstamo registrado: '{libro.titulo}' a '{usuario.nombre}'.")
            return prestamo
        except ValueError as e:
            print(f"Error en el formato de la fecha de préstamo: {e}")
            return None


    def registrar_devolucion(self, libro_isbn, usuario_id, fecha_devolucion_str):
        for prestamo in self.prestamos:
            if prestamo.libro.isbn == libro_isbn and prestamo.usuario.id_usuario == usuario_id and prestamo.fecha_devolucion is None:
                try:
                    fecha_devolucion = datetime.datetime.strptime(fecha_devolucion_str, '%Y-%m-%d').date()
                    multa = prestamo.calcular_multa(fecha_devolucion)
                    prestamo.registrar_devolucion(fecha_devolucion)
                    prestamo.libro.devolver()
                    prestamo.usuario.remover_libro_prestado(prestamo.libro)
                    print(f"Devolución registrada para '{prestamo.libro.titulo}'. Multa: {multa:.2f} euros.")
                    return multa
                except ValueError as e:
                    print(f"Error en el formato de la fecha de devolución: {e}")
                    return None
                except Exception as e:
                    print(f"Error al registrar devolución: {e}")
                    return None

        print(f"Error: No se encontró un préstamo activo para el libro con ISBN {libro_isbn} y usuario con ID {usuario_id}.")
        return None


    def calcular_estadisticas(self):
        total_libros = len(self.libros)
        libros_disponibles = sum(libro.cantidad for libro in self.libros.values())
        total_usuarios = len(self.usuarios)
        prestamos_activos = sum(1 for prestamo in self.prestamos if prestamo.fecha_devolucion is None)
        total_multas = sum(prestamo.calcular_multa(datetime.date.today()) for prestamo in self.prestamos if prestamo.fecha_devolucion is None)

        return {
            "total_libros": total_libros,
            "libros_disponibles": libros_disponibles,
            "total_usuarios": total_usuarios,
            "prestamos_activos": prestamos_activos,
            "total_multas_pendientes": total_multas
        }

    def generar_reporte_mensual(self, mes, anio):
        reporte = f"Reporte Mensual de la Biblioteca - {mes}/{anio}\n"
        reporte += "=" * 40 + "\n\n"

        prestamos_mes = [
            p for p in self.prestamos
            if p.fecha_prestamo.month == mes and p.fecha_prestamo.year == anio
        ]

        if prestamos_mes:
            reporte += "Detalle de Préstamos del Mes:\n"
            for prestamo in prestamos_mes:
                estado = "Activo" if prestamo.fecha_devolucion is None else f"Devuelto el {prestamo.fecha_devolucion}"
                multa = prestamo.calcular_multa(datetime.date.today() if prestamo.fecha_devolucion is None else prestamo.fecha_devolucion)
                reporte += f"- Libro: '{prestamo.libro.titulo}' (ISBN: {prestamo.libro.isbn})\n"
                reporte += f"  Usuario: '{prestamo.usuario.nombre}' (ID: {prestamo.usuario.id_usuario})\n"
                reporte += f"  Fecha Préstamo: {prestamo.fecha_prestamo}\n"
                reporte += f"  Estado: {estado}\n"
                reporte += f"  Multa calculada: {multa:.2f} euros\n"
                reporte += "-----\n"
        else:
            reporte += "No hubo préstamos registrados en este mes.\n"

        reporte += "\n" + "=" * 40 + "\n"
        reporte += "Estadísticas Generales:\n"
        estadisticas = self.calcular_estadisticas()
        for key, value in estadisticas.items():
            reporte += f"- {key.replace('_', ' ').title()}: {value}\n"

        return reporte


# Create the JSON file with sample data
sample_data = {
    "libros": [
        {"titulo": "Cien años de soledad", "autor": "Gabriel García Márquez", "isbn": "978-3-16-148410-0", "cantidad": 5},
        {"titulo": "1984", "autor": "George Orwell", "isbn": "978-0-345-33968-3", "cantidad": 3},
        {"titulo": "Un mundo feliz", "autor": "Aldous Huxley", "isbn": "978-0-06-112008-4", "cantidad": 2}
    ],
    "usuarios": [
        {"nombre": "Ana López", "id_usuario": "U001"},
        {"nombre": "Juan Pérez", "id_usuario": "U002"}
    ]
}

with open("datos_iniciales.json", "w") as f:
    json.dump(sample_data, f, indent=4)

# Instantiate Biblioteca and load data
biblioteca = Biblioteca()
biblioteca.cargar_datos_iniciales("datos_iniciales.json")

# Print loaded data
print("Libros cargados:")
for isbn, libro in biblioteca.libros.items():
    print(f"- {libro}")

print("\nUsuarios cargados:")
for id_usuario, usuario in biblioteca.usuarios.items():
    print(f"- {usuario}")

if __name__ == "__main__":
    # 2. Create an instance of the Biblioteca class.
    biblioteca = Biblioteca()

    # 3. Call the cargar_datos_iniciales method.
    print("Cargando datos iniciales...")
    biblioteca.cargar_datos_iniciales("datos_iniciales.json")
    print("Datos iniciales cargados.")

    # 4. Demonstrate searching for books.
    print("\nBuscando libro por título '1984':")
    resultados_titulo = biblioteca.buscar_libro('titulo', '1984')
    for libro in resultados_titulo:
        print(f"- Encontrado: {libro}")

    print("\nBuscando libro por autor 'Aldous Huxley':")
    resultados_autor = biblioteca.buscar_libro('autor', 'Aldous Huxley')
    for libro in resultados_autor:
        print(f"- Encontrado: {libro}")

    print("\nBuscando libro por ISBN '978-3-16-148410-0':")
    resultados_isbn = biblioteca.buscar_libro('isbn', '978-3-16-148410-0')
    for libro in resultados_isbn:
        print(f"- Encontrado: {libro}")

    # 5. Demonstrate registering a new user.
    print("\nRegistrando nuevo usuario 'Carlos Gómez' con ID 'U003':")
    nuevo_usuario = biblioteca.registrar_usuario("Carlos Gómez", "U003")
    if nuevo_usuario:
        print(f"Usuario registrado: {nuevo_usuario}")
    else:
        print("No se pudo registrar el usuario.")

    # 6. Demonstrate registering a loan.
    print("\nRegistrando préstamo del libro con ISBN '978-0-345-33968-3' al usuario con ID 'U001' en la fecha '2023-10-25':")
    prestamo_registrado = biblioteca.registrar_prestamo("978-0-345-33968-3", "U001", "2023-10-25")
    if prestamo_registrado:
        print(f"Préstamo registrado: {prestamo_registrado}")
    else:
        print("No se pudo registrar el préstamo.")

    # 7. Demonstrate registering a return.
    print("\nRegistrando devolución del libro con ISBN '978-0-345-33968-3' por el usuario con ID 'U001' en la fecha '2023-11-15':")
    multa_calculada = biblioteca.registrar_devolucion("978-0-345-33968-3", "U001", "2023-11-15")
    if multa_calculada is not None:
        print(f"Devolución procesada. Multa calculada: {multa_calculada:.2f}")
    else:
        print("No se pudo registrar la devolución.")

    # 8. Demonstrate calculating and printing statistics.
    print("\nCalculando estadísticas de la biblioteca:")
    estadisticas = biblioteca.calcular_estadisticas()
    for key, value in estadisticas.items():
        print(f"- {key.replace('_', ' ').title()}: {value}")

    # 9. Demonstrate generating a monthly report.
    print("\nGenerando reporte mensual para Noviembre de 2023:")
    reporte_nov_2023 = biblioteca.generar_reporte_mensual(11, 2023)
    print(reporte_nov_2023)

class Biblioteca:
    def __init__(self):
        self.libros = {}
        self.usuarios = {}
        self.prestamos = []

    def cargar_datos_iniciales(self, archivo):
        try:
            with open(archivo, 'r') as f:
                data = json.load(f)
                for libro_data in data.get('libros', []):
                    try:
                        libro = Libro(libro_data['titulo'], libro_data['autor'], libro_data['isbn'], libro_data['cantidad'])
                        self.libros[libro.isbn] = libro
                    except (ValueError, KeyError) as e:
                        print(f"Error al cargar libro: {e} en datos: {libro_data}")
                for usuario_data in data.get('usuarios', []):
                    try:
                        usuario = Usuario(usuario_data['nombre'], usuario_data['id_usuario'])
                        if usuario.id_usuario in self.usuarios:
                             print(f"Advertencia: Usuario con ID {usuario.id_usuario} duplicado, saltando.")
                             continue
                        self.usuarios[usuario.id_usuario] = usuario
                    except (ValueError, KeyError) as e:
                        print(f"Error al cargar usuario: {e} en datos: {usuario_data}")
        except FileNotFoundError:
            print(f"Error: Archivo no encontrado en {archivo}")
        except json.JSONDecodeError:
            print(f"Error: No se pudo decodificar el archivo JSON en {archivo}")
        except Exception as e:
            print(f"Error inesperado al cargar datos: {e}")

    def buscar_libro(self, criterio, valor):
        resultados = []
        criterio = criterio.lower()
        for libro in self.libros.values():
            if criterio == 'titulo' and valor.lower() in libro.titulo.lower():
                resultados.append(libro)
            elif criterio == 'autor' and valor.lower() in libro.autor.lower():
                resultados.append(libro)
            elif criterio == 'isbn' and valor.lower() == libro.isbn.lower():
                resultados.append(libro)
        return resultados

    def registrar_usuario(self, nombre, id_usuario):
        if id_usuario in self.usuarios:
            print(f"Error: El usuario con ID {id_usuario} ya existe.")
            return None
        try:
            usuario = Usuario(nombre, id_usuario)
            self.usuarios[id_usuario] = usuario
            return usuario
        except ValueError as e:
            print(f"Error al registrar usuario: {e}")
            return None

    def registrar_prestamo(self, libro_isbn, usuario_id, fecha_prestamo_str):
        if libro_isbn not in self.libros:
            print(f"Error: Libro con ISBN {libro_isbn} no encontrado.")
            return None
        if usuario_id not in self.usuarios:
            print(f"Error: Usuario con ID {usuario_id} no encontrado.")
            return None

        libro = self.libros[libro_isbn]
        usuario = self.usuarios[usuario_id]

        if not libro.disponible():
            print(f"Error: El libro '{libro.titulo}' no está disponible.")
            return None

        try:
            fecha_prestamo = datetime.datetime.strptime(fecha_prestamo_str, '%Y-%m-%d').date()
            prestamo = Prestamo(libro, usuario, fecha_prestamo)
            self.prestamos.append(prestamo)
            libro.prestar()
            usuario.agregar_libro_prestado(libro)
            print(f"Préstamo registrado: '{libro.titulo}' a '{usuario.nombre}'.")
            return prestamo
        except ValueError as e:
            print(f"Error en el formato de la fecha de préstamo: {e}")
            return None


    def registrar_devolucion(self, libro_isbn, usuario_id, fecha_devolucion_str):
        for prestamo in self.prestamos:
            if prestamo.libro.isbn == libro_isbn and prestamo.usuario.id_usuario == usuario_id and prestamo.fecha_devolucion is None:
                try:
                    fecha_devolucion = datetime.datetime.strptime(fecha_devolucion_str, '%Y-%m-%d').date()
                    multa = prestamo.calcular_multa(fecha_devolucion)
                    prestamo.registrar_devolucion(fecha_devolucion)
                    prestamo.libro.devolver()
                    prestamo.usuario.remover_libro_prestado(prestamo.libro)
                    print(f"Devolución registrada para '{prestamo.libro.titulo}'. Multa: {multa:.2f} euros.")
                    return multa
                except ValueError as e:
                    print(f"Error en el formato de la fecha de devolución: {e}")
                    return None
                except Exception as e:
                    print(f"Error al registrar devolución: {e}")
                    return None

        print(f"Error: No se encontró un préstamo activo para el libro con ISBN {libro_isbn} y usuario con ID {usuario_id}.")
        return None


    def calcular_estadisticas(self):
        total_libros = len(self.libros)
        libros_disponibles = sum(libro.cantidad for libro in self.libros.values())
        total_usuarios = len(self.usuarios)
        prestamos_activos = sum(1 for prestamo in self.prestamos if prestamo.fecha_devolucion is None)
        total_multas = sum(prestamo.calcular_multa(datetime.date.today()) for prestamo in self.prestamos if prestamo.fecha_devolucion is None)

        return {
            "total_libros": total_libros,
            "libros_disponibles": libros_disponibles,
            "total_usuarios": total_usuarios,
            "prestamos_activos": prestamos_activos,
            "total_multas_pendientes": total_multas
        }

    def generar_reporte_mensual(self, mes, anio):
        reporte = f"Reporte Mensual de la Biblioteca - {mes}/{anio}\n"
        reporte += "=" * 40 + "\n\n"

        prestamos_mes = [
            p for p in self.prestamos
            if p.fecha_prestamo.month == mes and p.fecha_prestamo.year == anio
        ]

        if prestamos_mes:
            reporte += "Detalle de Préstamos del Mes:\n"
            for prestamo in prestamos_mes:
                estado = "Activo" if prestamo.fecha_devolucion is None else f"Devuelto el {prestamo.fecha_devolucion}"
                multa = prestamo.calcular_multa(datetime.date.today() if prestamo.fecha_devolucion is None else prestamo.fecha_devolucion)
                reporte += f"- Libro: '{prestamo.libro.titulo}' (ISBN: {prestamo.libro.isbn})\n"
                reporte += f"  Usuario: '{prestamo.usuario.nombre}' (ID: {prestamo.usuario.id_usuario})\n"
                reporte += f"  Fecha Préstamo: {prestamo.fecha_prestamo}\n"
                reporte += f"  Estado: {estado}\n"
                reporte += f"  Multa calculada: {multa:.2f} euros\n"
                reporte += "-----\n"
        else:
            reporte += "No hubo préstamos registrados en este mes.\n"

        reporte += "\n" + "=" * 40 + "\n"
        reporte += "Estadísticas Generales:\n"
        estadisticas = self.calcular_estadisticas()
        for key, value in estadisticas.items():
            reporte += f"- {key.replace('_', ' ').title()}: {value}\n"

        return reporte

    def exportar_reporte_txt(self, mes, anio, nombre_archivo):
        reporte_content = self.generar_reporte_mensual(mes, anio)
        try:
            with open(nombre_archivo, 'w') as f:
                f.write(reporte_content)
            print(f"Reporte exportado exitosamente a '{nombre_archivo}'.")
        except IOError as e:
            print(f"Error al exportar el reporte a '{nombre_archivo}': {e}")

# Crear una instancia de la clase Biblioteca
biblioteca_export_test = Biblioteca()

# Cargar datos iniciales
biblioteca_export_test.cargar_datos_iniciales("datos_iniciales.json")

# Registre un préstamo de muestra para noviembre de 2023 para probar el informe
biblioteca_export_test.registrar_prestamo("978-0-345-33968-3", "U001", "2023-11-01")

# Exportar el informe de noviembre de 2023 a un archivo de texto
biblioteca_export_test.exportar_reporte_txt(11, 2023, "reporte_biblioteca_nov_2023.txt")