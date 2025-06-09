# 🔢 Simplex Solver: Calculadora de Programación Lineal

**Simplex Solver** es una aplicación de escritorio desarrollada en **Python** con **Tkinter** que permite resolver problemas de programación lineal utilizando el algoritmo Simplex. La aplicación ofrece una interfaz gráfica moderna e intuitiva para configurar y resolver problemas de maximización y minimización con múltiples restricciones.

---

## 🚀 Características

- 🎯 **Resolución Dual**: Soporte para problemas de maximización y minimización
- 📊 **Interfaz Gráfica Moderna**: GUI intuitiva construida con Tkinter y ttk
- 🔢 **Soporte de Fracciones**: Cálculos precisos utilizando aritmética de fracciones
- 📈 **Visualización de Tableaux**: Generación automática de imágenes de cada iteración
- 📝 **Proceso Detallado**: Visualización paso a paso del algoritmo Simplex
- ⚡ **Validación Inteligente**: Verificación automática de datos de entrada
- 💾 **Exportación**: Guardar tableaux como imágenes PNG
- 🎨 **Diseño Responsivo**: Interfaz adaptable con pestañas organizadas
- 🔍 **Análisis de Solución**: Estadísticas detalladas del proceso de resolución

---

## 📁 Estructura del Proyecto

```
.
├── app.py                     # Lógica principal del algoritmo Simplex
├── controlador_simplex.py     # Controlador principal de la aplicación
├── servicio_simplex.py        # Servicios de negocio y validaciones
├── vista_simplex.py           # Interfaz gráfica de usuario
├── main.py                    # Punto de entrada de la aplicación
├── requirements.txt           # Dependencias del proyecto
└── README.md                  # Este archivo
```

---

## 🛠️ Requisitos Previos

Antes de ejecutar la aplicación, asegúrate de tener instalado:

- **Python 3.8+**
- **pip** (gestor de paquetes de Python)

---

## ⚙️ Instalación

1. **Clona o descarga el repositorio**:
   ```bash
   git clone <url-del-repositorio>
   cd simplex-solver
   ```

2. **Instala las dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Ejecuta la aplicación**:
   ```bash
   python index.py
   ```

---

## 📋 Dependencias

Las siguientes librerías son requeridas (incluidas en `requirements.txt`):

- `matplotlib==3.10.3` - Generación de gráficos y visualizaciones
- `numpy==2.3.0` - Cálculos numéricos y matrices
- `pillow==11.2.1` - Procesamiento de imágenes
- `tabulate==0.9.0` - Formateo de tablas

---

## 🎮 Uso de la Aplicación

### 1. **Configuración del Problema**
- Selecciona el tipo de problema (Maximización/Minimización)
- Ingresa el número de variables
- Configura la función objetivo con sus coeficientes

### 2. **Definición de Restricciones**
- Agrega restricciones una por una
- Especifica coeficientes, tipo de desigualdad (≤, ≥, =) y término independiente
- Elimina restricciones individuales si es necesario

### 3. **Resolución**
- Haz clic en "Resolver" para ejecutar el algoritmo
- Visualiza el resumen de la solución en la pestaña principal
- Consulta el proceso detallado en "Proceso de Resolución"

### 4. **Exportación**
- Exporta los tableaux como imágenes PNG
- Guarda el proceso completo para documentación

---

## 💡 Ejemplo de Uso

**Problema de Maximización:**
```
Maximizar: 3x₁ + 2x₂
Sujeto a:
  x₁ + x₂ ≤ 4
  2x₁ + x₂ ≤ 5
  x₁, x₂ ≥ 0
```

**Resultado esperado:**
- x₁ = 1, x₂ = 3
- Valor óptimo = 9

---

## 🔧 Características Técnicas

### **Algoritmo Simplex**
- Implementación completa del método Simplex estándar
- Manejo de variables de holgura y artificiales
- Método Big M para restricciones de igualdad y ≥
- Detección automática de problemas infactibles

### **Validaciones**
- Verificación de formato de entrada
- Validación de coeficientes numéricos
- Control de problemas mal formulados

### **Visualización**
- Tableaux formateados con colores
- Resaltado de elementos pivote
- Estadísticas de iteraciones

---

## 🎨 Interfaz de Usuario

La aplicación cuenta con dos pestañas principales:

### **📊 Configurar y Resultados**
- Configuración del problema
- Entrada de datos
- Resumen de la solución

### **📈 Proceso de Resolución**
- Proceso paso a paso
- Tableaux de cada iteración
- Análisis detallado

---

## 🐛 Solución de Problemas

### **Errores Comunes:**

1. **"Coeficientes inválidos"**: Verifica que todos los campos contengan números válidos
2. **"Problema infactible"**: El problema no tiene solución factible
3. **"Error de exportación"**: Verifica permisos de escritura en la carpeta destino

### **Consejos:**
- Usa fracciones para mayor precisión (ej: 1/3 en lugar de 0.333)
- Asegúrate de que todas las restricciones estén bien formuladas
- Verifica que el problema tenga al menos una variable y una restricción

---

## 📊 Características de Salida

La aplicación proporciona:

- ✅ **Solución óptima** con valores de variables
- 📈 **Valor objetivo óptimo**
- 🔢 **Número de iteraciones realizadas**
- 📋 **Estadísticas del proceso**
- 🖼️ **Tableaux visuales exportables**
- ⚠️ **Detección de infactibilidad**

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

---

## 📌 Autor

Desarrollado con 💻 y ☕ por **Yusurus** y **FernandoM42**

📧 Contacto: **[yjru_at@hotmail.com]**

---

## 🙏 Agradecimientos

- Algoritmo Simplex basado en los fundamentos de George Dantzig
- Interfaz gráfica desarrollada con Tkinter
- Visualizaciones creadas con Matplotlib
