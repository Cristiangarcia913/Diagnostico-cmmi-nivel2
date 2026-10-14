# -*- coding: utf-8 -*-
# Programa para saber si cumplimos CMMI Nivel 2
# Hecho de forma muy basica y facil para clase

import tkinter as tk

# Las preguntas divididas en las 5 partes de CMMI
preguntas = [
    ("REQM - Requisitos", [
        ("Se escriben los requisitos?", "Apunta los requisitos en un documento."),
        ("Se relacionan con las pruebas?", "Haz una tabla para ver que prueba revisa cada requisito."),
        ("Se controlan los cambios?", "No cambies cosas sin avisar y apuntarlo antes."),
        ("Se revisan con el cliente?", "Queda con el cliente para revisar que todo este bien."),
        ("Estan guardados en un sitio accesible?", "Pon los archivos en una carpeta compartida.")
    ]),
    ("PP - Planificacion", [
        ("Hay fechas y calendario?", "Haz un calendario con las fechas de entrega."),
        ("Se sabe quien hace cada tarea?", "Apunta el nombre de la persona responsable de cada tarea."),
        ("Se piensan los posibles problemas?", "Haz una lista de cosas que podrian salir mal."),
        ("Hay dinero reservado por si acaso?", "Calcula un poco de dinero extra por si hay imprevistos."),
        ("El plan esta aprobado?", "Pide al profesor o cliente que de el visto bueno.")
    ]),
    ("PMC - Seguimiento", [
        ("Se mira el avance cada semana?", "Revisa una vez a la semana si vais a tiempo."),
        ("Se vigilan las horas y el dinero?", "Apunta si os estais pasando de horas de trabajo."),
        ("Se buscan soluciones si hay retrasos?", "Si vais tarde, cambiad cosas rapido para recuperar."),
        ("Se siguen vigilando los problemas?", "Vuelve a mirar la lista de problemas de vez en cuando."),
        ("Se hacen reuniones de balance?", "Haz una reunion corta al terminar cada parte grande.")
    ]),
    ("CM - Gestion de Cambios", [
        ("Se usa Git con ramas?", "Usa Git con ramas y no subas todo a lo loco."),
        ("Se ponen versiones (v1.0...)?", "Ponle version tipo v1.0 o v2.0 a cada entrega."),
        ("Se revisa el codigo antes de juntarlo?", "Que un companero revise el codigo antes de hacer merge."),
        ("Se hacen copias de seguridad?", "Guarda copias de seguridad a menudo."),
        ("Se apuntan cambios importantes?", "Apunta en un bloc de notas los cambios que hagas.")
    ]),
    ("PPQA - Calidad", [
        ("Hay reglas para programar bien?", "Poned unas normas basicas de como escribir el codigo."),
        ("Se prueba el programa?", "Prueba que los botones y funciones vayan antes de entregar."),
        ("Se apuntan los fallos que salen?", "Apunta los fallos en una lista para arreglarlos."),
        ("Alguien vigila que se hagan bien las cosas?", "Que alguien del equipo revise que se siguen los pasos."),
        ("Se revisa todo antes de entregar?", "Haz una revision final antes de la entrega definitiva.")
    ])
]

# Creamos la ventana y la abrimos maximizada para que ocupe toda la pantalla
ventana = tk.Tk()
ventana.title("Mi Test de CMMI Nivel 2")
ventana.state("zoomed")  # En Windows esto abre la ventana en pantalla completa

# Parte de arriba: Nombre del proyecto y boton de calcular a mano
arriba = tk.Frame(ventana, pady=10)
arriba.pack()

tk.Label(arriba, text="Nombre del proyecto:", font=("Arial", 11)).pack(side="left", padx=5)
caja_nombre = tk.Entry(arriba, width=25, font=("Arial", 11))
caja_nombre.insert(0, "Mi Proyecto")
caja_nombre.pack(side="left", padx=10)

# Ponemos un canvas con scroll para subir y bajar comodamente
canvas = tk.Canvas(ventana, highlightthickness=0)
scroll = tk.Scrollbar(ventana, orient="vertical", command=canvas.yview)
zona_preguntas = tk.Frame(canvas)

zona_preguntas.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
canvas.create_window((0, 0), window=zona_preguntas, anchor="nw")
canvas.configure(yscrollcommand=scroll.set)

# Esto permite subir y bajar con la rueda del raton en cualquier parte
def mover_rueda(evento):
    canvas.yview_scroll(int(-1 * (evento.delta / 120)), "units")

ventana.bind_all("<MouseWheel>", mover_rueda)

canvas.pack(side="top", fill="both", expand=True, padx=25, pady=5)
scroll.pack(side="right", fill="y")

# Lista para guardar los botones que marque el usuario
mis_respuestas = []

# Dibujamos las preguntas una a una
for nombre_seccion, lista_de_preguntas in preguntas:
    # Titulo de la seccion
    titulo_sec = tk.Label(zona_preguntas, text="=== " + nombre_seccion + " ===", font=("Arial", 11, "bold"), fg="blue")
    titulo_sec.pack(anchor="w", pady=(12, 4))
    
    for texto_preg, consejo in lista_de_preguntas:
        # Fila con la pregunta
        fila_preg = tk.Frame(zona_preguntas, pady=2)
        fila_preg.pack(anchor="w", fill="x")

        lbl = tk.Label(fila_preg, text=texto_preg, font=("Arial", 10))
        lbl.pack(anchor="w")
        
        # Variable para la opcion elegida: 1=Si, 2=A medias, 3=No
        opcion_elegida = tk.StringVar(value="1")
        mis_respuestas.append((nombre_seccion, consejo, opcion_elegida))
        
        # Fila de botones Si / A medias / No
        fila_botones = tk.Frame(fila_preg)
        fila_botones.pack(anchor="w", padx=15, pady=2)
        
        tk.Radiobutton(fila_botones, text="Si", variable=opcion_elegida, value="1").pack(side="left")
        tk.Radiobutton(fila_botones, text="A medias", variable=opcion_elegida, value="2").pack(side="left", padx=15)
        tk.Radiobutton(fila_botones, text="No", variable=opcion_elegida, value="3").pack(side="left")

# Esta funcion calcula la nota
def calcular():
    nombre = caja_nombre.get()
    if nombre == "":
        nombre = "Mi Proyecto"
        
    puntos = {}
    for seccion, _ in preguntas:
        puntos[seccion] = 0
        
    consejos_para_mejorar = []
    
    for seccion, consejo, opcion in mis_respuestas:
        valor = opcion.get()
        if valor == "1":
            puntos[seccion] = puntos[seccion] + 1
        elif valor == "2":
            puntos[seccion] = puntos[seccion] + 0.5
            consejos_para_mejorar.append(consejo)
        else:
            consejos_para_mejorar.append(consejo)
            
    texto = "RESULTADOS DE: " + nombre + "\n\n"
    
    secciones_aprobadas = 0
    for seccion in puntos:
        pts = puntos[seccion]
        porcentaje = (pts / 5) * 100
        
        if porcentaje >= 80:
            estado = "Aprobado"
            secciones_aprobadas = secciones_aprobadas + 1
        else:
            estado = "No llega al minimo"
            
        texto = texto + seccion + ": " + str(int(porcentaje)) + "% -> " + estado + "\n"
        
    texto = texto + "\n----------------------------------------\n"
    if secciones_aprobadas == 5:
        texto = texto + "ENHORABUENA: Cumple con CMMI Nivel 2!\n"
    else:
        texto = texto + "AVISO: No llega a Nivel 2 (hace falta 80% en todas las areas).\n"
        
    texto = texto + "----------------------------------------\n\n"
    texto = texto + "Cosas que deberias mejorar:\n"
    
    if len(consejos_para_mejorar) == 0:
        texto = texto + "- Ninguna, todo esta perfecto!\n"
    else:
        for c in consejos_para_mejorar:
            texto = texto + "- " + c + "\n"
            
    # Ventana para ver los resultados
    ventana_resultado = tk.Toplevel(ventana)
    ventana_resultado.title("Resultado")
    ventana_resultado.geometry("520x450")
    
    cuadro = tk.Text(ventana_resultado, wrap="word", padx=12, pady=12)
    cuadro.insert("1.0", texto)
    cuadro.pack(fill="both", expand=True)
    
    btn_cerrar = tk.Button(ventana_resultado, text="Cerrar", command=ventana_resultado.destroy)
    btn_cerrar.pack(pady=8)

# Boton para calcular puesto arriba al lado del nombre y tambien abajo
btn_arriba = tk.Button(arriba, text="Calcular nota", font=("Arial", 10, "bold"), bg="#d0e1fd", command=calcular)
btn_arriba.pack(side="left", padx=10)

btn_abajo = tk.Button(ventana, text="Calcular nota", font=("Arial", 11, "bold"), bg="#d0e1fd", command=calcular)
btn_abajo.pack(pady=10)

# Iniciamos el programa
ventana.mainloop()
