# PEC1 - Herramienta de diagnostico CMMI Nivel 2

Gestion de Proyectos Software 2026/27

Integrantes: Cristian Garcia Del Olmo, Izan Jimenez Jimenez, Jaime Cristobal Martin

## Requisitos

Python 3.9 o superior con tkinter (viene incluido en Windows y macOS; en Linux:
`sudo apt install python3-tk`).

## Ejecucion

Version 1 (no hay que instalar nada):

    python v1/diagnostico_cmmi_v1.py

Version 2:

    pip install reportlab
    python v2/diagnostico_cmmi_v2.py

Para usar el boton opcional "Ampliar con IA" de la version 2:

    pip install openai
    # Windows (PowerShell):  $env:OPENAI_API_KEY="tu_clave"
    # Linux/macOS:           export OPENAI_API_KEY="tu_clave"

Sin clave, todo funciona igual con las recomendaciones base.

## Uso

1. Escribe el nombre del proyecto.
2. Responde Si / Parcial / No en las 5 pestanas (REQM, PP, PMC, CM, PPQA).
3. "Diagnosticar esta KPA" muestra los apartados 1-4 de la pestana activa.
4. "Evaluar Nivel 2 completo" muestra los apartados 5-9 (necesita las 25 respuestas).
5. Exportar el informe (V1: .txt; V2: .pdf y .txt).

## Criterios

Si = 1, Parcial = 0,5, No = 0. Cumplimiento = suma / 5 x 100.
Implementada >= 80%, Parcial 50-79%, Deficiente < 50%.
Nivel 2 cumplido solo si las 5 KPAs estan implementadas.
