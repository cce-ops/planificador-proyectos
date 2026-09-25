# 📊 Planificador de Proyectos de Ingeniería

Aplicación web interactiva desarrollada con **Python y Streamlit** para la planificación, análisis y seguimiento de proyectos de ingeniería mediante técnicas **PERT, CPM, Gantt y método de Zaderenko**.

La herramienta permite introducir las actividades de un proyecto, definir sus relaciones de precedencia y duraciones, y obtener automáticamente información sobre la planificación temporal, el camino crítico, las holguras y la probabilidad de cumplimiento del proyecto.

## 🚀 Aplicación online

Puedes utilizar la aplicación directamente desde Streamlit:

👉 **[Abrir Planificador de Proyectos](https://planificador-proyectos.streamlit.app/)**

No es necesario instalar Python ni ninguna dependencia para utilizar la versión desplegada.

## 📁 Repositorio

Código fuente disponible en GitHub:

👉 **[cce-ops/planificador-proyectos](https://github.com/cce-ops/planificador-proyectos)**

---

## 🎯 Objetivo

El objetivo de este proyecto es proporcionar una herramienta sencilla e interactiva para aplicar técnicas de **planificación y gestión de proyectos de ingeniería**.

La aplicación permite transformar los datos de un proyecto en:

* 📅 Calendarios de ejecución.
* 📊 Diagramas de Gantt.
* 🔗 Redes de precedencias.
* 🔴 Identificación del camino crítico.
* ⏱️ Tiempos tempranos y tardíos.
* 📐 Cálculo de holguras.
* 📈 Estimación probabilística de la duración.
* 📋 Tablas de resultados.
* 🧮 Matrices de Zaderenko.

La aplicación está especialmente orientada a proyectos académicos y de ingeniería en los que sea necesario analizar la planificación temporal de un conjunto de actividades.

---

# 🛠️ Funcionalidades

La aplicación está dividida en dos modos de planificación:

## 1. 🟢 Modo Básico — Actividades y Precedencias

Este modo utiliza una representación **Activity on Node (AON)**.

El usuario introduce:

| Campo            | Descripción                                                |
| ---------------- | ---------------------------------------------------------- |
| **Tarea**        | Identificador de la actividad                              |
| **Duración**     | Duración de la actividad en días laborables                |
| **Predecesores** | Actividades que deben finalizar antes de comenzar la tarea |

También se puede seleccionar la fecha de inicio del proyecto.

### Cálculos realizados

A partir de las actividades introducidas, la aplicación construye automáticamente un grafo dirigido de precedencias y calcula:

* **ES — Early Start:** inicio más temprano.
* **EF — Early Finish:** finalización más temprana.
* **LS — Late Start:** inicio más tardío.
* **LF — Late Finish:** finalización más tardía.
* **Holgura total** de cada actividad.
* **Camino crítico**.
* **Duración total del proyecto**.
* **Fecha estimada de finalización**.

Las precedencias se procesan mediante un ordenamiento topológico del grafo. Si existe un ciclo en las precedencias, la aplicación muestra un mensaje de error.

### 📊 Resultados gráficos

El modo básico genera:

* Diagrama de **Gantt**.
* Grafo de precedencias tipo **PERT**.
* Tabla completa de resultados.

Las actividades críticas se identifican visualmente en los gráficos.

---

# 2. 🔵 Modo Avanzado — Nodos y Método de Zaderenko

El modo avanzado utiliza una representación **Activity on Arrow (AOA)** y permite trabajar con actividades definidas entre sucesos/nodos.

Para cada actividad se introducen:

| Campo           | Descripción                   |
| --------------- | ----------------------------- |
| **Actividad**   | Identificador de la actividad |
| **i (Origen)**  | Nodo inicial                  |
| **j (Destino)** | Nodo final                    |
| **t_opt**       | Tiempo optimista              |
| **t_prob**      | Tiempo más probable           |
| **t_pes**       | Tiempo pesimista              |

A partir de estos valores se calcula el tiempo esperado mediante la expresión PERT:

$$
t_e = \frac{t_{opt} + 4t_{prob} + t_{pes}}{6}
$$

También se calcula la varianza de cada actividad:

$$
\sigma^2 = \left(\frac{t_{pes}-t_{opt}}{6}\right)^2
$$

Estos cálculos permiten realizar posteriormente una estimación probabilística de la duración del proyecto.

### 📐 Método de Zaderenko

La aplicación genera una **matriz de Zaderenko** con los tiempos correspondientes a los diferentes nodos del proyecto.

También calcula:

* Tiempos tempranos de los sucesos.
* Tiempos tardíos de los sucesos.
* Holguras.
* Camino crítico.
* Duración esperada del proyecto.
* Varianza del proyecto.
* Desviación estándar.

---

## 📈 Análisis probabilístico

El modo avanzado permite introducir un **plazo objetivo** y calcular la probabilidad estadística de finalizar el proyecto dentro de dicho plazo.

La aplicación utiliza la distribución normal para obtener esta probabilidad:

$$
P(T \leq T_{objetivo}) =
\Phi\left(
\frac{T_{objetivo}-T_e}{\sigma}
\right)
$$

donde:

* \(T_e\) = duración esperada del proyecto.
* \(\sigma\) = desviación estándar.
* \(T_{objetivo}\) = plazo objetivo.
* \(\Phi\) = función de distribución acumulada de la normal.

El resultado se muestra directamente en la interfaz como porcentaje de probabilidad de cumplimiento.

---

# 📊 Visualizaciones

La aplicación genera diferentes representaciones gráficas para facilitar la interpretación de los resultados.

### Diagrama de Gantt

Permite visualizar:

* Inicio de cada actividad.
* Finalización.
* Duración.
* Actividades críticas.

### Red PERT

Representa gráficamente las relaciones entre actividades o sucesos.

### Matriz de Zaderenko

Permite analizar los tiempos de los diferentes sucesos del proyecto.

### Tablas de resultados

Los resultados numéricos se presentan mediante tablas interactivas que facilitan su consulta y análisis.

---

# 🧰 Tecnologías utilizadas

El proyecto está desarrollado principalmente con Python.

### Lenguaje

* 🐍 **Python**

### Framework

* **Streamlit** — desarrollo de la interfaz web interactiva.

### Análisis de datos

* **Pandas**
* **NumPy**

### Análisis de grafos

* **NetworkX**

### Visualización

* **Plotly**
* **Matplotlib**

### Estadística

* **SciPy**

Estas dependencias están especificadas en `requirements.txt`.

---

# 📂 Estructura del proyecto

```text
planificador-proyectos/
│
├── app.py
├── requirements.txt
└── README.md
```

### `app.py`

Archivo principal de la aplicación Streamlit. Contiene:

* Interfaz de usuario.
* Entrada y edición de actividades.
* Construcción de grafos.
* Cálculos PERT/CPM.
* Método de Zaderenko.
* Cálculo del camino crítico.
* Análisis probabilístico.
* Generación de diagramas Gantt y PERT.

### `requirements.txt`

Contiene las dependencias necesarias para ejecutar la aplicación:

```text
streamlit
pandas
networkx
plotly
matplotlib
scipy
numpy
```

---

# 💻 Instalación local

Si quieres ejecutar el proyecto en tu ordenador, primero clona el repositorio:

```bash
git clone https://github.com/cce-ops/planificador-proyectos.git
```

Accede al directorio:

```bash
cd planificador-proyectos
```

## Crear un entorno virtual

### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## Instalar dependencias

```bash
pip install -r requirements.txt
```

## Ejecutar la aplicación

```bash
streamlit run app.py
```

Una vez iniciada, Streamlit mostrará la dirección local desde la que se puede acceder a la aplicación.

---

# 📝 Cómo utilizar la aplicación

## Modo Básico

1. Accede a la pestaña **"Modo Básico (Actividades y Precedencias)"**.
2. Introduce las actividades del proyecto.
3. Indica la duración de cada actividad.
4. Introduce los predecesores correspondientes.
5. Selecciona la fecha de inicio.
6. Pulsa **"Calcular Proyecto Básico"**.
7. Consulta:

   * Duración total.
   * Fecha de finalización.
   * Tabla de resultados.
   * Camino crítico.
   * Diagrama de Gantt.
   * Grafo PERT.

### Ejemplo

```text
Tarea | Duración | Predecesores
A     | 2        |
B     | 3        | A
C     | 3        | A
D     | 4        | B
E     | 3        | C
F     | 5        | D,E
```

Las actividades pueden tener varios predecesores separados mediante comas:

```text
D,E
```

---

# 🔬 Ejemplo del Modo Avanzado

Un proyecto puede definirse mediante actividades entre nodos:

```text
Actividad | i | j | t_opt | t_prob | t_pes
A         | 1 | 2 | 1     | 1      | 1
B         | 1 | 3 | 2     | 2      | 2
C         | 2 | 4 | 3     | 3      | 3
D         | 2 | 5 | 6     | 6      | 6
```

La aplicación calcula automáticamente los tiempos esperados y las varianzas para realizar posteriormente el análisis PERT.

---

# ⚠️ Consideraciones

### Días laborables

La planificación temporal utiliza una semana laboral de:

```text
Lunes → Viernes
```

Los sábados y domingos no se consideran días laborables en el cálculo de las fechas.

### Precedencias

En el modo básico, las relaciones entre actividades deben formar una red acíclica. Si se introduce una dependencia circular, la aplicación detectará el problema y mostrará un mensaje de error.

### Datos de entrada

Las duraciones y tiempos introducidos deben utilizar valores numéricos válidos para que los cálculos puedan realizarse correctamente.

---

# 🎓 Aplicaciones académicas

Esta herramienta puede utilizarse como apoyo para estudiar y practicar conceptos relacionados con:

* Gestión de proyectos.
* Organización industrial.
* Planificación de proyectos.
* Ingeniería de proyectos.
* Métodos PERT y CPM.
* Diagramas de Gantt.
* Camino crítico.
* Redes de actividades.
* Método de Zaderenko.
* Análisis estadístico de proyectos.

También puede utilizarse para comprobar manualmente ejercicios de planificación y analizar el efecto que tienen diferentes duraciones y precedencias sobre la duración total de un proyecto.

---

# 🔄 Flujo general de cálculo

```text
             DATOS DEL PROYECTO
                     │
                     ▼
          ┌─────────────────────┐
          │ Actividades / Nodos │
          └──────────┬──────────┘
                     │
                     ▼
             Construcción
              del grafo
                     │
                     ▼
          ┌─────────────────────┐
          │ Cálculo de tiempos  │
          │ tempranos y tardíos │
          └──────────┬──────────┘
                     │
                     ▼
              Holguras y
             camino crítico
                     │
                     ▼
          ┌─────────────────────┐
          │ Gantt + PERT +      │
          │ tablas de resultados│
          └─────────────────────┘
                     │
                     ▼
            Análisis probabilístico
              (modo avanzado)
```

---

# 🌐 Despliegue

La aplicación está desplegada mediante **Streamlit** y puede utilizarse directamente desde:

👉 https://planificador-proyectos.streamlit.app/

El repositorio de GitHub contiene el código fuente utilizado para la aplicación.

---

# 🤝 Contribuciones

Las contribuciones son bienvenidas.

Si quieres proponer mejoras:

1. Realiza un fork del repositorio.
2. Crea una nueva rama:

```bash
git checkout -b feature/nueva-funcionalidad
```

3. Realiza los cambios.
4. Haz commit:

```bash
git commit -m "Añadir nueva funcionalidad"
```

5. Sube la rama:

```bash
git push origin feature/nueva-funcionalidad
```

6. Abre un **Pull Request**.

---

# 💡 Posibles mejoras futuras

Algunas funcionalidades que podrían incorporarse en futuras versiones son:

* [ ] Exportación de resultados a Excel.
* [ ] Exportación de diagramas a PDF o imagen.
* [ ] Importación de proyectos desde Excel/CSV.
* [ ] Guardado y carga de proyectos.
* [ ] Inclusión de festivos en el calendario laboral.
* [ ] Configuración personalizada de calendarios.
* [ ] Comparación entre diferentes escenarios.
* [ ] Análisis de costes de proyecto.
* [ ] Recursos asociados a las actividades.
* [ ] Nivelación de recursos.
* [ ] Mejoras en la representación de redes PERT.
* [ ] Validación más completa de los datos de entrada.
* [ ] Historial de proyectos.
* [ ] Interfaz multilingüe.

---

# 📄 Licencia

Actualmente, el repositorio no especifica una licencia de software. Si el proyecto va a distribuirse o reutilizarse públicamente, se recomienda añadir un archivo `LICENSE` con la licencia elegida.

---

## 👨‍💻 Proyecto

**Planificador de Proyectos de Ingeniería**

Desarrollado con:

**Python · Streamlit · Pandas · NetworkX · Plotly · Matplotlib · SciPy · NumPy**

---

⭐ Si este proyecto te resulta útil, puedes darle una estrella al repositorio en GitHub.

[![GitHub](https://img.shields.io/badge/GitHub-Repository-black?logo=github)](https://github.com/cce-ops/planificador-proyectos)
[![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B?logo=streamlit\&logoColor=white)](https://planificador-proyectos.streamlit.app/)
