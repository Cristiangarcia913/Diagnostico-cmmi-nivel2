# 📊 CMMI Level 2 Diagnostic & Software Quality Audit Tool

> **Herramienta interactiva de auditoría y evaluación de madurez de procesos de software basada en el modelo internacional CMMI Nivel 2 (Gestionado), desarrollada en Python con interfaz gráfica, visualización estadística y generación de informes ejecutivos en PDF.**

<p align="left">
  <a href="LICENSE">
    <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT" />
  </a>
  <img src="https://img.shields.io/badge/Python-3.9+-3776AB?logo=python&logoColor=white" alt="Python 3.9+" />
  <img src="https://img.shields.io/badge/GUI-Tkinter-green?logo=python" alt="Tkinter GUI" />
  <img src="https://img.shields.io/badge/PDF_Engine-ReportLab-red" alt="ReportLab" />
  <img src="https://img.shields.io/badge/AI_Assisted-OpenAI_API-412991?logo=openai&logoColor=white" alt="OpenAI API" />
</p>

---

## 🎯 Objetivo y Contexto

En la ingeniería de software profesional, la calidad del producto final depende de la disciplina y madurez de los procesos del equipo de desarrollo. Esta aplicación automatiza la auditoría de un proyecto u organización respecto a las **Áreas de Proceso Clave (KPAs)** del nivel 2 de CMMI (*Capability Maturity Model Integration*).

Desarrollada en el marco de la asignatura de **Gestión de Proyectos de Software** (3º del Grado en Ingeniería Informática, **Universidad Camilo José Cela**).

---

## 🔍 Áreas de Proceso Evaluadas (KPAs de CMMI Nivel 2)

La herramienta evalúa cuantitativa y cualitativamente las 7 KPAs esenciales:

1. **Gestión de Requisitos (REQM):** Trazabilidad, análisis de impacto y control de cambios en requisitos.
2. **Planificación del Proyecto (PP):** Estimación de esfuerzos, cronogramas, riesgos y asignación presupuestaria.
3. **Seguimiento y Control del Proyecto (PMC):** Monitorización de hitos, desviaciones y toma de acciones correctivas.
4. **Gestión de Acuerdos con Proveedores (SAM):** Selección, contratos y seguimiento de componentes tercerizados.
5. **Medición y Análisis (MA):** Definición de métricas de rendimiento, calidad y almacenamiento de datos.
6. **Aseguramiento de la Calidad del Proceso y del Producto (PPQA):** Auditorías objetivas y revisiones de no conformidad.
7. **Gestión de la Configuración (CM):** Líneas base, control de versiones e integridad del repositorio de artefactos.

---

## ✨ Características Principales

- 🖥️ **Interfaz Gráfica Guiada:** Formulario estructurado para calificar prácticas y registrar observaciones por pregunta.
- 📊 **Visualización Estadística en Tiempo Real:** Gráficos de barras que reflejan el porcentaje de cumplimiento por KPA frente a los umbrales críticos del **50%** y **80%**.
- 📄 **Exportación de Informes en PDF:** Motor con `reportlab` que genera un informe ejecutivo completo con portada, tablas de puntuación, nivel global alcanzado y recomendaciones de mejora.
- 🤖 **Motor de Recomendaciones con IA (Opcional):** Integración con la API de OpenAI en un hilo en segundo plano (*threading*) para sugerir planes de acción personalizados sin bloquear la interfaz.

---

## 🚀 Instalación y Uso

### 1. Requisitos Previos
* Python 3.9 o superior.

### 2. Instalación de Dependencias
```bash
git clone https://github.com/Cristiangarcia913/Diagnostico-cmmi-nivel2.git
cd Diagnostico-cmmi-nivel2
pip install -r requirements.txt
```

### 3. Ejecución
```bash
python diagnostico_cmmi_v2.py
```

*(Opcional: Si deseas habilitar el asistente de IA para recomendaciones ampliadas, exporta previamente tu clave: `export OPENAI_API_KEY="tu-clave"` o en Windows `set OPENAI_API_KEY=tu-clave`).*

---

## 📂 Estructura del Repositorio

```text
├── diagnostico_cmmi_v2.py      # Versión integral: GUI + Motor estadístico + PDF + IA
├── diagnostico_cmmi_v1_gui.py  # Versión base inicial
├── Memoria_PEC1_...pdf          # Memoria técnica y justificación metodológica
├── requirements.txt            # Dependencias del proyecto
└── LICENSE                     # Licencia abierta MIT
```

---

## 👥 Autores

* **Cristian García Del Olmo** ([@Cristiangarcia913](https://github.com/Cristiangarcia913))
* **Izan Jiménez Jiménez**
* **Jaime Cristóbal Martín**

Grado en Ingeniería Informática — **Universidad Camilo José Cela (UCJC)**

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Consulta el archivo [LICENSE](LICENSE) para más información.
