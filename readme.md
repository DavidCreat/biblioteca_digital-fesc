## 🧩 Características principales

- Registro y búsqueda de **libros** por título, autor o ISBN.  
- Gestión de **usuarios** y control de duplicados.  
- Registro de **préstamos** y **devoluciones** con control de fechas.  
- Cálculo automático de **multas** por retraso en las devoluciones.  
- Carga de **datos iniciales** desde un archivo JSON.  
- Generación y exportación de **reportes mensuales** en formato `.txt`.  
- Cálculo de **estadísticas generales** (total de libros, préstamos activos, multas pendientes, etc.).  

---

## 🧠 Clases principales

### `Libro`
Representa un libro con atributos como título, autor, ISBN y cantidad disponible.  
Métodos principales:
- `disponible()` – Verifica si hay ejemplares disponibles.  
- `prestar()` – Resta una unidad al stock.  
- `devolver()` – Suma una unidad al stock.

### `Usuario`
Representa a un usuario de la biblioteca.  
Métodos principales:
- `agregar_libro_prestado(libro)`  
- `remover_libro_prestado(libro)`

### `Prestamo`
Gestiona un préstamo entre un libro y un usuario.  
Métodos principales:
- `calcular_multa(fecha_actual, dias_permitidos=14, costo_por_dia=0.5)`  
- `registrar_devolucion(fecha_devolucion)`

### `Biblioteca`
Clase principal que coordina la gestión de todos los datos.  
Métodos destacados:
- `cargar_datos_iniciales(archivo)`  
- `buscar_libro(criterio, valor)`  
- `registrar_usuario(nombre, id_usuario)`  
- `registrar_prestamo(libro_isbn, usuario_id, fecha_prestamo_str)`  
- `registrar_devolucion(libro_isbn, usuario_id, fecha_devolucion_str)`  
- `calcular_estadisticas()`  
- `generar_reporte_mensual(mes, anio)`  
- `exportar_reporte_txt(mes, anio, nombre_archivo)`

---

## ⚙️ evidencia
<img width="1352" height="576" alt="image" src="https://github.com/user-attachments/assets/7a4c2d4d-3adb-464d-9500-60574bce1dca" />
<img width="1362" height="578" alt="image" src="https://github.com/user-attachments/assets/fc42a54a-4ed6-4b94-ad76-d61378da2710" />
<img width="267" height="74" alt="image" src="https://github.com/user-attachments/assets/73a17fa8-dae3-4bdf-aba0-328fb2f56b07" />

