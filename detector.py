from datetime import datetime

# Parte 4 - Paso 1: Función para registrar la respuesta en respuesta.log
def registrar_respuesta(usuario):
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("respuesta.log", "a", encoding="utf-8") as archivo:
        archivo.write(f"{fecha},USUARIO_BLOQUEADO,{usuario}\n")
    return fecha

intentos = {}

# Leer los logs generados por la aplicación Flask
try:
    with open("eventos.log", "r", encoding="utf-8") as archivo:
        for linea in archivo:
            if not linea.strip():
                continue
            fecha_str, tipo, usuario = linea.strip().split(",")
            
            if tipo == "LOGIN_FALLIDO":
                if usuario not in intentos:
                    intentos[usuario] = []
                intentos[usuario].append(fecha_str)
except FileNotFoundError:
    print("Error: El archivo eventos.log aún no se ha generado. Realiza intentos fallidos primero.")
    exit()

# Criterio 8, 9 y 10: Procesar alertas y calcular tiempos métricos
for usuario, registros in intentos.items():
    if len(registros) >= 3:
        print("\n========================================")
        print("ALERTA DE SEGURIDAD")
        print(f"Usuario: {usuario}")
        print(f"Intentos fallidos: {len(registros)}")
        print(f"Primer intento: {registros[0]}")
        print(f"Detección: {registros[2]}")
        
        # Conversión de tiempos para cálculo matemático
        inicio = datetime.strptime(registros[0], "%Y-%m-%d %H:%M:%S")
        deteccion = datetime.strptime(registros[2], "%Y-%m-%d %H:%M:%S")
        
        # Calcular MTTD (Tiempo Medio de Detección)
        mttd = (deteccion - inicio).total_seconds()
        print(f"MTTD: {mttd} segundos")
        
        # Aplicar respuesta automática simulada (Bloqueo)
        fecha_respuesta = registrar_respuesta(usuario)
        print("Acción aplicada: bloqueo de usuario")
        print(f"Respuesta: {fecha_respuesta}")
        
        # Calcular MTTR (Tiempo Medio de Respuesta)
        respuesta_dt = datetime.strptime(fecha_respuesta, "%Y-%m-%d %H:%M:%S")
        mttr = (respuesta_dt - deteccion).total_seconds()
        print(f"MTTR: {mttr} segundos")
        print("========================================")