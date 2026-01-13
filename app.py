import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

# --------------------------------------------------
# CONFIGURACIÓN GENERAL
# --------------------------------------------------
st.set_page_config(
    page_title="CMMS Pro – Flota Frigorífica",
    page_icon="❄️",
    layout="wide"
)

st.markdown("""
<style>
body {background-color: #0E1117;}
[data-testid="metric-container"] {
    background-color: #161B22;
    padding: 15px;
    border-radius: 12px;
}
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# CARGA / SIMULACIÓN DE DATOS
# --------------------------------------------------
@st.cache_data
def cargar_datos():
    vehiculos = pd.DataFrame({
        "id": range(1, 51),
        "placa": [f"TRK-{i:03d}" for i in range(1, 51)],
        "estado": np.random.choice(["Operativo", "Mantenimiento"], 50, p=[0.9, 0.1]),
        "kilometraje": np.random.randint(3000, 30000, 50)
    })

    equipos = pd.DataFrame({
        "id": range(1, 51),
        "modelo": "Thermo King",
        "estado": np.random.choice(["Operativo", "Mantenimiento"], 50, p=[0.88, 0.12]),
        "horas": np.random.randint(100, 2000, 50)
    })

    repuestos = pd.DataFrame([
        {"id": 1, "nombre": "Filtro Aceite Motor", "activo": "Camión", "stock": 40, "min": 8},
        {"id": 2, "nombre": "Pastillas de Freno", "activo": "Camión", "stock": 25, "min": 10},
        {"id": 3, "nombre": "Filtro Aire Thermo King", "activo": "Thermo King", "stock": 18, "min": 6},
        {"id": 4, "nombre": "Sensor de Temperatura", "activo": "Thermo King", "stock": 10, "min": 4},
    ])

    ordenes = pd.DataFrame(columns=[
        "idOT", "tipo", "activo", "placa", "falla",
        "km_horas", "repuesto", "cantidad", "fecha"
    ])

    return vehiculos, equipos, repuestos, ordenes


vehiculos, equipos, repuestos, ordenes = cargar_datos()

# --------------------------------------------------
# KPIs PRINCIPALES
# --------------------------------------------------
disp_veh = round((vehiculos[vehiculos.estado == "Operativo"].shape[0] / len(vehiculos)) * 100, 1)
disp_eq = round((equipos[equipos.estado == "Operativo"].shape[0] / len(equipos)) * 100, 1)
disp_rep = round((repuestos[repuestos.stock > repuestos.min].shape[0] / len(repuestos)) * 100, 1)

# MTBF / MTTR
fallas = ordenes[ordenes["tipo"] == "Correctivo"]
mtbf = round(720 / len(fallas), 2) if len(fallas) > 0 else "N/A"
mttr = round(np.random.uniform(2, 6), 2) if len(fallas) > 0 else "N/A"

# --------------------------------------------------
# DASHBOARD
# --------------------------------------------------
st.title("🚚❄️ CMMS Pro – Gestión de Flota Frigorífica")

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Disp. Vehículos", f"{disp_veh}%")
k2.metric("Disp. Equipos Frío", f"{disp_eq}%")
k3.metric("Disp. Repuestos", f"{disp_rep}%")
k4.metric("MTBF (h)", mtbf)
k5.metric("MTTR (h)", mttr)

# --------------------------------------------------
# TELEMETRÍA SIMULADA
# --------------------------------------------------
st.subheader("🌡️ Temperatura Promedio – Thermo King")
temperaturas = -18 + np.random.normal(0, 0.4, 24)
st.line_chart(temperaturas)

# --------------------------------------------------
# REGISTRO DE ORDEN DE TRABAJO
# --------------------------------------------------
st.subheader("🛠️ Orden de Trabajo")

tipo_ot = st.selectbox("Tipo de OT", ["Preventivo", "Correctivo"])
activo = st.selectbox("Activo", ["Camión", "Thermo King"])
placa = st.selectbox("Placa / Equipo", vehiculos["placa"] if activo == "Camión" else equipos["id"])
km_horas = st.number_input("Kilometraje / Horas", 0, 50000)

falla = st.selectbox(
    "Falla (si aplica)",
    [
        "No aplica",
        "Refrigeración insuficiente",
        "Sensor de temperatura",
        "Fuga de refrigerante",
        "Falla eléctrica",
        "Filtro obstruido"
    ]
)

repuesto_sel = st.selectbox("Repuesto", repuestos[repuestos.activo == activo]["nombre"])

# Consumo técnico
if km_horas >= 20000:
    consumo = 3
elif km_horas >= 10000:
    consumo = 2
else:
    consumo = 1

if st.button("Registrar OT"):
    idx = repuestos[repuestos.nombre == repuesto_sel].index[0]

    if repuestos.loc[idx, "stock"] < consumo:
        st.error("Stock insuficiente")
    else:
        repuestos.loc[idx, "stock"] -= consumo

        ordenes.loc[len(ordenes)] = [
            len(ordenes) + 1, tipo_ot, activo, placa,
            falla, km_horas, repuesto_sel, consumo, datetime.now()
        ]

        st.success("Orden registrada y repuesto descontado")

# --------------------------------------------------
# KARDEX DE REPUESTOS
# --------------------------------------------------
st.subheader("📦 Kardex de Repuestos")
st.dataframe(repuestos, use_container_width=True)

# --------------------------------------------------
# HISTORIAL DE ÓRDENES
# --------------------------------------------------
st.subheader("📋 Historial de Órdenes")
st.dataframe(ordenes, use_container_width=True)

# --------------------------------------------------
# ALERTAS
# --------------------------------------------------
alertas = repuestos[repuestos.stock <= repuestos.min]
if not alertas.empty:
    st.error("🚨 Repuestos en nivel crítico")
    st.dataframe(alertas)
