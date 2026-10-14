# -*- coding: utf-8 -*-
"""
Herramienta de diagnóstico CMMI Nivel 2 - VERSIÓN 2 (desarrollada con ayuda de IA)
Gestión de Proyectos Software 2026/27 - PEC1

Cubre los 9 apartados del enunciado y añade respecto a la versión 1:
  - Observación opcional por pregunta (como en el ejemplo del enunciado).
  - Gráfico de barras de cumplimiento por KPA con los umbrales del 50% y 80%.
  - Exportación del informe a PDF (reportlab) además de texto.
  - Lógica separada de la interfaz: evaluar_proyecto() devuelve datos estructurados
    y de ellos salen tanto el texto en pantalla como el PDF.
  - Botón OPCIONAL de recomendaciones ampliadas con IA (API de OpenAI). Sin clave
    de API la herramienta funciona igual con las recomendaciones base.
  - La llamada a la API se hace en un hilo para no bloquear la ventana.

Instalación:  pip install -r requirements.txt
Ejecución:    python diagnostico_cmmi_v2.py
IA opcional:  definir la variable de entorno OPENAI_API_KEY antes de ejecutar.
"""

import os
import queue
import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
from xml.sax.saxutils import escape

MODELO_IA = "gpt-4o-mini"

# =============================================================================
# 1. DATOS: opciones de respuesta, umbrales y preguntas por KPA
# =============================================================================

# Valor numérico de cada respuesta
OPCIONES = {"Sí": 1.0, "Parcial": 0.5, "No": 0.0}

# Umbrales indicados en el enunciado
UMBRAL_IMPLEMENTADA = 80   # >= 80%  -> Implementada
UMBRAL_PARCIAL = 50        # 50-79%  -> Parcialmente implementada; <50% -> Deficiente

# Cada KPA tiene 5 preguntas. Cada pregunta es una tupla (texto, recomendación).
# La recomendación se muestra cuando la respuesta es "No" o "Parcial".
KPAS = [
    {
        "sigla": "REQM",
        "nombre": "Gestión de Requisitos",
        "preguntas": [
            ("¿Se documentan los requisitos funcionales y no funcionales?",
             "Formalizar la documentación completa de requisitos (funcionales y "
             "no funcionales) en un documento de especificación versionado."),
            ("¿Existe trazabilidad entre requisitos, entregables y pruebas?",
             "Implementar una matriz de trazabilidad que relacione requisitos "
             "con entregables y casos de prueba."),
            ("¿Se gestiona formalmente el cambio de requisitos?",
             "Definir un proceso formal de control de cambios: solicitud, "
             "análisis de impacto, aprobación y registro."),
            ("¿Se revisan los requisitos con los stakeholders?",
             "Establecer revisiones periódicas con los stakeholders para validar "
             "los requisitos antes de cada fase o iteración."),
            ("¿Se almacenan los requisitos en un repositorio accesible?",
             "Centralizar los requisitos aprobados en un repositorio accesible, "
             "con control de versiones y de accesos."),
        ],
    },
    {
        "sigla": "PP",
        "nombre": "Planificación de Proyectos",
        "preguntas": [
            ("¿Existe un cronograma detallado con estimación de esfuerzo?",
             "Elaborar un cronograma detallado (por ejemplo, un Gantt) con la "
             "estimación de esfuerzo de cada módulo o tarea."),
            ("¿Se definen y asignan los recursos humanos y técnicos necesarios?",
             "Definir y asignar los recursos humanos y técnicos mediante una "
             "matriz de roles y disponibilidad."),
            ("¿Se identifican y documentan los riesgos iniciales?",
             "Crear un registro de riesgos con probabilidad, impacto y plan de "
             "respuesta para cada uno."),
            ("¿Se elabora un presupuesto detallado con margen de contingencia?",
             "Elaborar un presupuesto detallado que incluya una reserva de "
             "contingencia y una reserva de gestión."),
            ("¿El plan del proyecto es aprobado formalmente por el sponsor?",
             "Obtener la aprobación formal del plan por parte del sponsor y los "
             "stakeholders (por ejemplo, un acta de proyecto firmada)."),
        ],
    },
    {
        "sigla": "PMC",
        "nombre": "Seguimiento y Control de Proyectos",
        "preguntas": [
            ("¿Se realiza un seguimiento semanal del avance respecto al plan?",
             "Realizar un seguimiento periódico (semanal) del avance real "
             "frente a la línea base del plan."),
            ("¿Se miden y analizan las desviaciones de coste y tiempo?",
             "Usar métricas de avance (porcentaje de tareas completadas, "
             "desviaciones, SPI/CPI) y analizar las desviaciones."),
            ("¿Se documentan las acciones correctivas ante retrasos?",
             "Documentar las acciones correctivas, con su responsable, su "
             "impacto y su cierre."),
            ("¿Se revisan periódicamente los riesgos durante la ejecución?",
             "Revisar y actualizar periódicamente el registro de riesgos "
             "durante la ejecución del proyecto."),
            ("¿Se realizan revisiones de hito al finalizar fases clave?",
             "Realizar revisiones de hito con la dirección y el cliente al "
             "cerrar cada fase clave."),
        ],
    },
    {
        "sigla": "CM",
        "nombre": "Gestión de Configuración",
        "preguntas": [
            ("¿Se usa control de versiones con una política de ramas definida?",
             "Formalizar el uso de control de versiones (Git) con ramas "
             "definidas (main, develop, feature)."),
            ("¿Se identifican y etiquetan las versiones de forma unívoca?",
             "Identificar y etiquetar cada versión de forma unívoca "
             "(versionado semántico, por ejemplo v1.0.0)."),
            ("¿Existe un procedimiento formal para aprobar cambios en producción?",
             "Establecer un procedimiento formal de aprobación (pull request "
             "con revisión por pares) antes de integrar en producción."),
            ("¿Se realizan backups periódicos de código, datos y configuración?",
             "Automatizar los backups periódicos de código, base de datos y "
             "configuración, y probar su restauración."),
            ("¿Se documentan las modificaciones de configuración e infraestructura?",
             "Documentar los cambios de configuración e infraestructura "
             "(servidores, variables de entorno) y mantener una política de "
             "gestión de configuración."),
        ],
    },
    {
        "sigla": "PPQA",
        "nombre": "Aseguramiento de Calidad",
        "preguntas": [
            ("¿Se definen métricas y estándares de calidad claros?",
             "Definir criterios y métricas de calidad para cada entrega y "
             "recogerlos en un Plan de Calidad."),
            ("¿Se ejecutan pruebas sistemáticas (unitarias, integración)?",
             "Implementar pruebas sistemáticas (unitarias, de integración y de "
             "seguridad) y automatizarlas en el proceso de integración continua."),
            ("¿Se registran y analizan los defectos para hallar su causa raíz?",
             "Registrar los defectos en un gestor de incidencias y analizarlos "
             "para mejorar los procesos."),
            ("¿Se realizan auditorías independientes del proceso?",
             "Designar un responsable de QA independiente que audite "
             "periódicamente el cumplimiento de los procesos."),
            ("¿Se verifica que los entregables cumplen los criterios de aceptación?",
             "Verificar los entregables contra criterios de aceptación "
             "definidos antes de cada entrega."),
        ],
    },
]


COLORES = {"Implementada": "#4CAF50", "Parcialmente implementada": "#FFC107",
           "Deficiente": "#E53935"}


# =============================================================================
# 2. LÓGICA (devuelve datos estructurados; no depende de tkinter)
# =============================================================================

def calcular_porcentaje(respuestas):
    """Media de los valores de las respuestas, en %."""
    return sum(OPCIONES[r] for r in respuestas) / len(respuestas) * 100


def obtener_estado(pct):
    if pct >= UMBRAL_IMPLEMENTADA:
        return "Implementada"
    if pct >= UMBRAL_PARCIAL:
        return "Parcialmente implementada"
    return "Deficiente"


def prioridad(pct):
    return "Alta" if pct < UMBRAL_PARCIAL else "Media"


def evaluar_kpa(kpa, respuestas, observaciones):
    """Evalúa una KPA y devuelve un diccionario con todo lo necesario para el informe."""
    pct = calcular_porcentaje(respuestas)
    detalle = []
    ausentes, parciales = [], []
    for (texto, rec), r, obs in zip(kpa["preguntas"], respuestas, observaciones):
        detalle.append({"pregunta": texto, "respuesta": r, "observacion": obs})
        if r == "No":
            ausentes.append(rec)
        elif r == "Parcial":
            parciales.append(rec + " (hoy la práctica es solo parcial: completarla)")
    recs = ausentes + parciales
    return {
        "sigla": kpa["sigla"], "nombre": kpa["nombre"], "pct": pct,
        "estado": obtener_estado(pct), "detalle": detalle, "recomendaciones": recs,
        "principal": recs[0] if recs else
        "Mantener las prácticas actuales y conservar la evidencia documental.",
    }


def evaluar_proyecto(proyecto, respuestas, observaciones):
    """Evalúa las 5 KPAs y calcula apartados 5-9."""
    kpas = [evaluar_kpa(k, respuestas[k["sigla"]], observaciones[k["sigla"]]) for k in KPAS]
    conteo = {
        "implementadas": sum(1 for k in kpas if k["estado"] == "Implementada"),
        "parciales": sum(1 for k in kpas if k["estado"] == "Parcialmente implementada"),
        "deficientes": sum(1 for k in kpas if k["estado"] == "Deficiente"),
    }
    cumple = conteo["implementadas"] == len(kpas)
    pendientes = sorted((k for k in kpas if k["estado"] != "Implementada"),
                        key=lambda k: k["pct"])
    plan = [{"prioridad": prioridad(k["pct"]), "kpa": k["nombre"], "pct": k["pct"],
             "acciones": k["recomendaciones"]} for k in pendientes]
    media = sum(k["pct"] for k in kpas) / len(kpas)
    return {"proyecto": proyecto, "kpas": kpas, "conteo": conteo, "cumple": cumple,
            "plan": plan, "media": media,
            "conclusion": redactar_conclusion(proyecto, kpas, cumple, media)}


def redactar_conclusion(proyecto, kpas, cumple, media):
    if cumple:
        return (f"El proyecto \"{proyecto}\" cumple los requisitos del nivel 2 de CMMI: "
                "todas las KPAs están implementadas. Se recomienda mantener las prácticas "
                "y conservar la evidencia documental para una evaluación formal.")
    pendientes = [k["nombre"] for k in sorted(kpas, key=lambda k: k["pct"])
                  if k["estado"] != "Implementada"]
    deficientes = [k["nombre"] for k in kpas if k["estado"] == "Deficiente"]
    txt = f"El proyecto \"{proyecto}\" "
    txt += ("está en transición hacia el nivel 2 " if media >= UMBRAL_PARCIAL
            else "está todavía lejos del nivel 2 ")
    txt += (f"(cumplimiento medio {media:.0f}%), pero necesita mejorar en: "
            + ", ".join(pendientes) + " para cumplir completamente los requisitos del modelo CMMI.")
    if deficientes:
        txt += (" Las KPAs deficientes (" + ", ".join(deficientes)
                + ") requieren actuación inmediata.")
    return txt


# ------------------------------------------------------------------ texto plano
def texto_kpa(ev):
    """Apartados 1-4 de una KPA en texto."""
    t = ["=" * 72, f"KPA: {ev['nombre']} ({ev['sigla']})", "=" * 72, "",
         "1. FORMULARIO DE EVALUACIÓN"]
    for i, d in enumerate(ev["detalle"], 1):
        t.append(f"   Pregunta {i}: {d['pregunta']}")
        extra = f" ({d['observacion']})" if d["observacion"] else ""
        t.append(f"      Respuesta: {d['respuesta']}{extra}")
    t += ["", "2. DIAGNÓSTICO AUTOMÁTICO",
          f"   Cumplimiento estimado de la KPA \"{ev['nombre']}\": {ev['pct']:.0f}%", "",
          "3. RECOMENDACIONES AUTOMÁTICAS"]
    if ev["recomendaciones"]:
        t += [f"   {i}. {r}" for i, r in enumerate(ev["recomendaciones"], 1)]
    else:
        t.append("   Ninguna: todas las prácticas clave están implantadas.")
    t += ["", "4. RESULTADO FINAL POR KPA",
          f"   Diagnóstico de la KPA: {ev['nombre']}",
          f"   - Nivel de cumplimiento: {ev['pct']:.0f}%",
          f"   - Estado: {ev['estado']}",
          f"   - Recomendación: {ev['principal']}", ""]
    return "\n".join(t)


def texto_global(ev):
    """Apartados 5-9 en texto."""
    c = ev["conteo"]
    t = ["=" * 72, f"DIAGNÓSTICO CMMI NIVEL 2 - PROYECTO: {ev['proyecto']}", "=" * 72, "",
         "5. EVALUACIÓN PARA TODAS LAS KPA",
         f"   {'KPA':<38}{'Cumplimiento':>13}   Estado", "   " + "-" * 64]
    for k in ev["kpas"]:
        t.append(f"   {k['nombre']:<38}{k['pct']:>12.0f}%   {k['estado']}")
    t += ["", "6. DIAGNÓSTICO GENERAL PARA TODAS LAS KPA",
          f"   - KPAs completamente implementadas: {c['implementadas']}",
          f"   - KPAs parcialmente implementadas: {c['parciales']}",
          f"   - KPAs deficientes: {c['deficientes']}", "",
          "7. VERIFICACIÓN DE CUMPLIMIENTO DEL NIVEL 2",
          "   Para cumplir el nivel 2 de CMMI, todas las KPAs del nivel deben estar",
          f"   implementadas de forma consistente (>= {UMBRAL_IMPLEMENTADA}%).",
          "   Resultado: " + ("CUMPLE el nivel 2" if ev["cumple"]
                              else "NO CUMPLE completamente el nivel 2"), "",
          "8. RECOMENDACIONES PARA ALCANZAR EL NIVEL 2"]
    if not ev["plan"]:
        t.append("   No hay recomendaciones pendientes: todas las KPAs están implementadas.")
    for i, p in enumerate(ev["plan"], 1):
        t.append(f"   {i}. {p['kpa']} (prioridad {p['prioridad'].lower()}, {p['pct']:.0f}%):")
        t += [f"      - {a}" for a in p["acciones"]]
    t += ["", "9. CONCLUSIÓN", "   " + ev["conclusion"], ""]
    return "\n".join(t)


def informe_completo_texto(ev, ia_texto=""):
    partes = [f"INFORME DE DIAGNÓSTICO CMMI NIVEL 2\nProyecto: {ev['proyecto']}\n"
              f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n"]
    partes += [texto_kpa(k) for k in ev["kpas"]]
    partes.append(texto_global(ev))
    if ia_texto:
        partes.append("RECOMENDACIONES AMPLIADAS CON IA\n" + ia_texto + "\n")
    return "\n".join(partes)


# ------------------------------------------------------------------------- PDF
def _limpio(texto):
    """Escapa XML y sustituye caracteres que Helvetica no puede dibujar."""
    texto = texto.replace("**", "").replace("#", "")
    texto = texto.encode("cp1252", "replace").decode("cp1252")
    return escape(texto).replace("\n", "<br/>")


def exportar_pdf(ev, ruta, ia_texto=""):
    """Genera el informe completo en PDF con reportlab."""
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import cm
    from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                    TableStyle, PageBreak)

    est = getSampleStyleSheet()
    doc = SimpleDocTemplate(ruta, pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm,
                            topMargin=2 * cm, bottomMargin=2 * cm,
                            title="Informe CMMI Nivel 2")

    def P(texto, estilo="BodyText"):
        return Paragraph(_limpio(texto), est[estilo])

    def tabla(filas, anchos, cabecera=True):
        t = Table(filas, colWidths=anchos, repeatRows=1 if cabecera else 0)
        estilo = [("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                  ("VALIGN", (0, 0), (-1, -1), "TOP")]
        if cabecera:
            estilo.append(("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#DDDDDD")))
        t.setStyle(TableStyle(estilo))
        return t

    h = []
    h.append(P("Informe de Diagnóstico CMMI Nivel 2", "Title"))
    h.append(P(f"Proyecto: {ev['proyecto']}"))
    h.append(P(f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}"))
    h.append(Spacer(1, 12))

    # Apartados 1-4 por KPA
    for k in ev["kpas"]:
        h.append(P(f"KPA: {k['nombre']} ({k['sigla']})", "Heading2"))
        filas = [[P("Pregunta"), P("Respuesta"), P("Observación")]]
        for d in k["detalle"]:
            filas.append([P(d["pregunta"]), P(d["respuesta"]), P(d["observacion"] or "-")])
        h.append(tabla(filas, [8.5 * cm, 2.5 * cm, 6 * cm]))
        h.append(Spacer(1, 6))
        h.append(Paragraph(f"<b>Cumplimiento:</b> {k['pct']:.0f}% &nbsp;&nbsp; "
                           f"<b>Estado:</b> {escape(k['estado'])}", est["BodyText"]))
        h.append(P("Recomendaciones:", "Heading4"))
        if k["recomendaciones"]:
            for i, r in enumerate(k["recomendaciones"], 1):
                h.append(P(f"{i}. {r}"))
        else:
            h.append(P("Ninguna: todas las prácticas clave están implantadas."))
        h.append(Spacer(1, 10))

    # Apartados 5-9
    h.append(PageBreak())
    h.append(P("Evaluación global del Nivel 2", "Heading1"))
    h.append(P("5. Evaluación para todas las KPA", "Heading2"))
    filas = [[P("KPA"), P("Cumplimiento"), P("Estado")]]
    for k in ev["kpas"]:
        filas.append([P(k["nombre"]), P(f"{k['pct']:.0f}%"), P(k["estado"])])
    h.append(tabla(filas, [8 * cm, 3 * cm, 6 * cm]))

    c = ev["conteo"]
    h.append(P("6. Diagnóstico general", "Heading2"))
    h.append(P(f"KPAs completamente implementadas: {c['implementadas']}"))
    h.append(P(f"KPAs parcialmente implementadas: {c['parciales']}"))
    h.append(P(f"KPAs deficientes: {c['deficientes']}"))

    h.append(P("7. Verificación de cumplimiento del Nivel 2", "Heading2"))
    h.append(P("Para cumplir el nivel 2 de CMMI, todas las KPAs deben estar implementadas "
               f"de forma consistente (>= {UMBRAL_IMPLEMENTADA}%)."))
    h.append(P("Resultado: " + ("CUMPLE el nivel 2" if ev["cumple"]
                                else "NO CUMPLE completamente el nivel 2")))

    h.append(P("8. Recomendaciones para alcanzar el Nivel 2", "Heading2"))
    if not ev["plan"]:
        h.append(P("No hay recomendaciones pendientes."))
    for i, p in enumerate(ev["plan"], 1):
        h.append(P(f"{i}. {p['kpa']} (prioridad {p['prioridad'].lower()}, {p['pct']:.0f}%)",
                   "Heading4"))
        for a in p["acciones"]:
            h.append(P("- " + a))

    h.append(P("9. Conclusión", "Heading2"))
    h.append(P(ev["conclusion"]))

    if ia_texto:
        h.append(P("Recomendaciones ampliadas con IA", "Heading2"))
        h.append(P(ia_texto))

    doc.build(h)


# --------------------------------------------------------------------------- IA
def construir_prompt(ev):
    """Prompt que se envía a la IA con los resultados reales de la evaluación."""
    lineas = [f"Proyecto evaluado: {ev['proyecto']}", "Resultados por KPA de CMMI Nivel 2:"]
    for k in ev["kpas"]:
        lineas.append(f"- {k['nombre']}: {k['pct']:.0f}% ({k['estado']})")
        for d in k["detalle"]:
            if d["respuesta"] != "Sí":
                obs = f" Observación: {d['observacion']}" if d["observacion"] else ""
                lineas.append(f"    * {d['pregunta']} -> {d['respuesta']}.{obs}")
    lineas.append("")
    lineas.append("Genera: 1) recomendaciones específicas y adaptadas al proyecto para cada "
                  "KPA que no esté implementada; 2) un plan de acción por pasos ordenado por "
                  "prioridad. Responde en español, en texto plano, en menos de 300 palabras.")
    return "\n".join(lineas)


# =============================================================================
# 3. INTERFAZ GRÁFICA
# =============================================================================

class AppDiagnostico:
    def __init__(self, root):
        self.root = root
        self.root.title("Diagnóstico CMMI Nivel 2 - Versión 2 (desarrollada con IA)")
        self.root.geometry("1000x820")

        self.var_proyecto = tk.StringVar()
        self.vars_resp = {}     # sigla -> [StringVar]
        self.vars_obs = {}      # sigla -> [StringVar]
        self.ultimo = None      # última evaluación completa calculada
        self.ia_texto = ""      # texto devuelto por la IA (si se ha pedido)
        self.cola = queue.Queue()

        self.crear_widgets()

    # ---------------------------------------------------------------- widgets
    def crear_widgets(self):
        tk.Label(self.root, text="Diagnóstico de cumplimiento CMMI Nivel 2",
                 font=("Helvetica", 16, "bold")).pack(pady=(10, 4))

        fila = tk.Frame(self.root)
        fila.pack(fill="x", padx=12, pady=4)
        tk.Label(fila, text="Proyecto / equipo:").pack(side="left")
        tk.Entry(fila, textvariable=self.var_proyecto, width=80).pack(side="left", padx=6)

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="x", padx=10, pady=6)
        for kpa in KPAS:
            marco = ttk.Frame(self.notebook)
            self.notebook.add(marco, text=kpa["sigla"])
            tk.Label(marco, text=f"{kpa['nombre']} ({kpa['sigla']})",
                     font=("Helvetica", 12, "bold")).pack(anchor="w", padx=10, pady=3)
            self.vars_resp[kpa["sigla"]] = []
            self.vars_obs[kpa["sigla"]] = []
            for i, (texto, _) in enumerate(kpa["preguntas"], 1):
                tk.Label(marco, text=f"{i}. {texto}", wraplength=940,
                         justify="left").pack(anchor="w", padx=14, pady=(3, 0))
                var = tk.StringVar(value="")
                obs = tk.StringVar(value="")
                self.vars_resp[kpa["sigla"]].append(var)
                self.vars_obs[kpa["sigla"]].append(obs)
                linea = tk.Frame(marco)
                linea.pack(anchor="w", padx=34, fill="x")
                for opcion in OPCIONES:
                    tk.Radiobutton(linea, text=opcion, variable=var,
                                   value=opcion).pack(side="left", padx=4)
                tk.Label(linea, text="  Observación:").pack(side="left")
                tk.Entry(linea, textvariable=obs, width=55).pack(side="left", padx=4)

        acciones = tk.Frame(self.root)
        acciones.pack(fill="x", padx=10, pady=4)
        tk.Button(acciones, text="Diagnosticar esta KPA (1-4)",
                  command=self.diagnosticar_kpa_actual).pack(side="left", padx=3)
        tk.Button(acciones, text="Evaluar Nivel 2 completo (5-9)",
                  command=self.evaluar_nivel2).pack(side="left", padx=3)
        self.btn_ia = tk.Button(acciones, text="Ampliar con IA (opcional)",
                                command=self.pedir_ia)
        self.btn_ia.pack(side="left", padx=3)
        tk.Button(acciones, text="Exportar PDF",
                  command=lambda: self.exportar("pdf")).pack(side="left", padx=3)
        tk.Button(acciones, text="Exportar TXT",
                  command=lambda: self.exportar("txt")).pack(side="left", padx=3)
        tk.Button(acciones, text="Limpiar", command=self.limpiar).pack(side="left", padx=3)

        self.lienzo = tk.Canvas(self.root, height=130, bg="white",
                                highlightthickness=1, highlightbackground="#999")
        self.lienzo.pack(fill="x", padx=10, pady=4)

        marco_txt = tk.Frame(self.root)
        marco_txt.pack(fill="both", expand=True, padx=10, pady=6)
        barra = tk.Scrollbar(marco_txt)
        barra.pack(side="right", fill="y")
        self.salida = tk.Text(marco_txt, wrap="word", font=("Courier", 10),
                              yscrollcommand=barra.set)
        self.salida.pack(side="left", fill="both", expand=True)
        barra.config(command=self.salida.yview)

    # --------------------------------------------------------------- utilidades
    def nombre_proyecto(self):
        return self.var_proyecto.get().strip() or "Proyecto sin nombre"

    def mostrar(self, texto):
        self.salida.delete("1.0", tk.END)
        self.salida.insert(tk.END, texto)

    def leer(self, kpa):
        """Devuelve (respuestas, observaciones) de una KPA o None si falta alguna respuesta."""
        sig = kpa["sigla"]
        resp = [v.get() for v in self.vars_resp[sig]]
        faltan = [str(i) for i, r in enumerate(resp, 1) if r not in OPCIONES]
        if faltan:
            messagebox.showwarning("Faltan respuestas",
                                   f"En {sig} faltan las preguntas: {', '.join(faltan)}")
            return None
        return resp, [v.get().strip() for v in self.vars_obs[sig]]

    def evaluar_todo(self):
        respuestas, observaciones = {}, {}
        for kpa in KPAS:
            leido = self.leer(kpa)
            if leido is None:
                return None
            respuestas[kpa["sigla"]], observaciones[kpa["sigla"]] = leido
        self.ultimo = evaluar_proyecto(self.nombre_proyecto(), respuestas, observaciones)
        return self.ultimo

    def dibujar_grafico(self, ev):
        c = self.lienzo
        c.delete("all")
        c.update_idletasks()
        ancho = max(c.winfo_width(), 600)
        alto_total = 130
        base, alto = alto_total - 22, alto_total - 40
        for umbral in (UMBRAL_PARCIAL, UMBRAL_IMPLEMENTADA):
            y = base - alto * umbral / 100
            c.create_line(0, y, ancho, y, dash=(3, 3), fill="#888")
            c.create_text(4, y - 6, text=f"{umbral}%", anchor="w", fill="#555")
        n = len(ev["kpas"])
        col = ancho / n
        for i, k in enumerate(ev["kpas"]):
            x0, x1 = i * col + col * 0.25, i * col + col * 0.75
            y = base - alto * k["pct"] / 100
            c.create_rectangle(x0, y, x1, base, fill=COLORES[k["estado"]], outline="")
            c.create_text((x0 + x1) / 2, y - 8, text=f"{k['pct']:.0f}%")
            c.create_text((x0 + x1) / 2, base + 11, text=k["sigla"])

    # ---------------------------------------------------------------- acciones
    def diagnosticar_kpa_actual(self):
        kpa = KPAS[self.notebook.index(self.notebook.select())]
        leido = self.leer(kpa)
        if leido is None:
            return
        ev = evaluar_kpa(kpa, leido[0], leido[1])
        self.mostrar(texto_kpa(ev))

    def evaluar_nivel2(self):
        ev = self.evaluar_todo()
        if ev is None:
            return
        self.mostrar(texto_global(ev) + (
            "\nRECOMENDACIONES AMPLIADAS CON IA\n" + self.ia_texto if self.ia_texto else ""))
        self.dibujar_grafico(ev)

    def exportar(self, formato):
        ev = self.evaluar_todo()
        if ev is None:
            return
        ruta = filedialog.asksaveasfilename(
            defaultextension="." + formato,
            filetypes=[("PDF", "*.pdf")] if formato == "pdf" else [("Texto", "*.txt")])
        if not ruta:
            return
        try:
            if formato == "pdf":
                exportar_pdf(ev, ruta, self.ia_texto)
            else:
                with open(ruta, "w", encoding="utf-8") as f:
                    f.write(informe_completo_texto(ev, self.ia_texto))
        except ImportError:
            messagebox.showerror("Falta reportlab",
                                 "Instala la dependencia con: pip install reportlab")
            return
        messagebox.showinfo("Exportado", f"Informe guardado en:\n{ruta}")

    # --- IA opcional (hilo + cola para no bloquear la ventana)
    def pedir_ia(self):
        ev = self.evaluar_todo()
        if ev is None:
            return
        if not os.getenv("OPENAI_API_KEY"):
            messagebox.showinfo("IA no configurada",
                                "Define la variable de entorno OPENAI_API_KEY para usar "
                                "esta función. El resto de la herramienta funciona sin ella.")
            return
        self.btn_ia.config(state="disabled")
        self.mostrar("Consultando a la IA, espera unos segundos...")
        threading.Thread(target=self._hilo_ia, args=(construir_prompt(ev),),
                         daemon=True).start()
        self.root.after(300, self._esperar_ia)

    def _hilo_ia(self, prompt):
        try:
            from openai import OpenAI          # openai >= 1.0
            cliente = OpenAI()
            r = cliente.chat.completions.create(
                model=MODELO_IA,
                messages=[
                    {"role": "system",
                     "content": "Eres un auditor experto en CMMI Nivel 2 y calidad de software."},
                    {"role": "user", "content": prompt}])
            self.cola.put(("ok", r.choices[0].message.content))
        except Exception as e:                  # sin red, clave inválida, etc.
            self.cola.put(("error", str(e)))

    def _esperar_ia(self):
        try:
            tipo, dato = self.cola.get_nowait()
        except queue.Empty:
            self.root.after(300, self._esperar_ia)
            return
        self.btn_ia.config(state="normal")
        if tipo == "ok":
            self.ia_texto = dato
            self.mostrar(texto_global(self.ultimo) +
                         "\nRECOMENDACIONES AMPLIADAS CON IA\n" + dato)
        else:
            self.mostrar("No se pudo obtener respuesta de la IA:\n" + dato +
                         "\n\nEl diagnóstico base sigue siendo válido.")

    def limpiar(self):
        for sig in self.vars_resp:
            for v in self.vars_resp[sig] + self.vars_obs[sig]:
                v.set("")
        self.ultimo, self.ia_texto = None, ""
        self.lienzo.delete("all")
        self.salida.delete("1.0", tk.END)


if __name__ == "__main__":
    ventana = tk.Tk()
    AppDiagnostico(ventana)
    ventana.mainloop()
