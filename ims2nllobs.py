import re
import os
from datetime import datetime, timedelta

def extraer_fecha_y_hora_evento(lineas):
    for linea in lineas:
        if re.match(r'\d{4}/\d{2}/\d{2}', linea.strip()):
            partes = linea.strip().split()
            fecha_str = partes[0]  # yyyy/mm/dd
            hora_str = partes[1]   # hh:mm:ss.ss
            dt_evento = datetime.strptime(f"{fecha_str} {hora_str}", "%Y/%m/%d %H:%M:%S.%f")
            return dt_evento
    raise ValueError("No se pudo encontrar la fecha/hora del evento.")

def parsear_linea_ims(linea, dt_evento, fecha_evento, fecha_siguiente):
    station = linea[0:5].strip()
    phase = linea[19:27].strip()
    time_str = linea[28:40].strip()

    try:
        t_obj = datetime.strptime(time_str, "%H:%M:%S.%f")
    except ValueError:
        return None

    hora_arribo = t_obj.time()

    if hora_arribo >= dt_evento.time():
        fecha_nllobs = fecha_evento.strftime("%Y%m%d")
    else:
        fecha_nllobs = fecha_siguiente.strftime("%Y%m%d")

    hhmm = t_obj.strftime("%H%M")
    ss_ssss = f"{t_obj.second}.{int(t_obj.microsecond / 100):04d}"

    return f"{station:<5}   ?    ?    ? {phase:<7} ? {fecha_nllobs} {hhmm} {ss_ssss} GAU  -1.00e+00 -1.00e+00 -1.00e+00 -1.00e+00"

def convertir_ims_a_nllobs(archivo_entrada, carpeta_salida):
    with open(archivo_entrada, 'r') as f:
        lineas = f.readlines()

    try:
        dt_evento = extraer_fecha_y_hora_evento(lineas)
    except ValueError as e:
        print(f"[!] Error en {archivo_entrada}: {e}")
        return

    fecha_evento = dt_evento.date()
    fecha_siguiente = fecha_evento + timedelta(days=1)

    # Generar nombre de archivo de salida: yyyymmdd_hhmmss.nllobs
    nombre_salida = dt_evento.strftime("%Y%m%d_%H%M%S.nllobs")
    ruta_salida = os.path.join(carpeta_salida, nombre_salida)

    nllobs_lines = []
    encabezado_encontrado = False

    for linea in lineas:
        if encabezado_encontrado:
            if linea.strip() == "":
                continue
            if re.match(r'^\w{4,5}\s+\d', linea):
                convertida = parsear_linea_ims(linea, dt_evento, fecha_evento, fecha_siguiente)
                if convertida:
                    nllobs_lines.append(convertida)
        elif linea.strip().startswith("Sta") and "Phase" in linea:
            encabezado_encontrado = True

    if not nllobs_lines:
        print(f"[!] No se encontraron líneas válidas en {archivo_entrada}")
        return

    os.makedirs(carpeta_salida, exist_ok=True)
    with open(ruta_salida, 'w') as f:
        for l in nllobs_lines:
            f.write(l + '\n')

    print(f"[✓] {os.path.basename(archivo_entrada)} → {nombre_salida} ({len(nllobs_lines)} líneas)")

def convertir_carpeta_ims(carpeta_entrada, carpeta_salida):
    archivos = [f for f in os.listdir(carpeta_entrada) if f.lower().endswith('.ims')]
    if not archivos:
        print(f"[!] No se encontraron archivos .ims en: {carpeta_entrada}")
        return

    for archivo in archivos:
        ruta_entrada = os.path.join(carpeta_entrada, archivo)
        convertir_ims_a_nllobs(ruta_entrada, carpeta_salida)

# === USO DE EJEMPLO ===
if __name__ == "__main__":
    carpeta_entrada = "datos_ims"       # Carpeta donde están los .ims
    carpeta_salida = "salida_nllobs"    # Carpeta de salida para los .nllobs
    convertir_carpeta_ims(carpeta_entrada, carpeta_salida)

