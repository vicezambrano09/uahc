import streamlit as st
import pandas as pd
import plotly.express as px

# Logo y título
st.image("https://campusvirtual.academia.cl/pluginfile.php/265/block_html/content/logo-web-bottom.png")
st.title("📘 Rendimiento Académico Regional")
st.markdown("Introducción a la programación con Python y R")

# Cargar datos
promedio = pd.read_csv("data/promedio.csv", encoding='latin-1')
simce = pd.read_csv("data/simce.csv", encoding='latin-1')

# Diccionario para regiones
regiones_interes = {
    "Atacama": {
        "Copiapó": ["Copiapó", "Tierra Amarilla", "Caldera"],
        "Chañaral": ["Chañaral", "Diego de Almagro"],
        "Huasco": ["Vallenar", "Freirina", "Huasco", "Alto del Carmen"]
    },
    "Coquimbo": {
        "Elqui": ["La Serena", "Coquimbo", "Vicuña", "Paihuano", "Andacollo"],
        "Limarí": ["Ovalle", "Monte Patria", "Combarbalá", "Punitaqui", "Río Hurtado"],
        "Choapa": ["Illapel", "Salamanca", "Los Vilos", "Canela"]
    },
    "Libertador General Bernardo O'Higgins": {
        "Cachapoal": ["Rancagua", "Machalí", "Requínoa", "Rengo"],
        "Colchagua": ["San Fernando", "Santa Cruz", "Chépica", "Nancagua"],
        "Cardenal Caro": ["Pichilemu", "Marchigüe", "Navidad"]
    },
    "Biobío": {
        "Concepción": ["Concepción", "Talcahuano", "Hualpén", "Coronel", "San Pedro de la Paz"],
        "Biobío": ["Los Ángeles", "Mulchén", "Nacimiento"],
        "Arauco": ["Curanilahue", "Lebu", "Cañete", "Arauco"]
    },
    "Los Ríos": {
        "Valdivia": ["Valdivia", "Lanco", "Panguipulli", "Máfil"],
        "Ranco": ["La Unión", "Río Bueno", "Futrono", "Lago Ranco"]
    },
    "Región Metropolitana": {
        "Santiago": ["Santiago", "Providencia", "Ñuñoa", "Las Condes"],
        "Maipo": ["San Bernardo", "Buin", "Paine"],
        "Cordillera": ["Puente Alto", "Pirque", "San José de Maipo"],
        "Chacabuco": ["Colina", "Lampa", "Tiltil"],
        "Melipilla": ["Melipilla", "Curacaví", "María Pinto"],
        "Talagante": ["Peñaflor", "Talagante", "El Monte"]
    }
}

#SIDEBAR: 
st.sidebar.title("🔍panel de metricas buscadas\nResultados SIMCE")

region = st.sidebar.selectbox("Regiones", list(regiones_interes.keys()))
provincia = st.sidebar.selectbox("Provincias", list(regiones_interes[region].keys()))
comuna = st.sidebar.selectbox("Comunas", regiones_interes[region][provincia])

asignatura = st.sidebar.radio("Asignatura:", ["Lenguaje", "Matemáticas"])

st.sidebar.write("Samir.Caro")
st.sidebar.write("Vicente.Zambrano")
st.sidebar.write("jorge.Sliva")

#  FILTRADO DE DATOS 

# SIMCE por comuna
simce_comuna = simce[simce["comuna"].str.lower() == comuna.lower()]

# Promedios nacionales (sin comuna)
if asignatura == "Lenguaje":
    promedio_nacional = promedio.rename(columns={"lenguaje": "Promedio"})
    simce_comuna = simce_comuna.rename(columns={"lenguaje": "Puntaje"})
else:
    promedio_nacional = promedio.rename(columns={"matematicas": "Promedio"})
    simce_comuna = simce_comuna.rename(columns={"matematicas": "Puntaje"})

# grafico 
st.subheader(f"Evolución anual de {asignatura} en {comuna}")

fig = px.line(
    promedio_nacional,
    x="agno",
    y="Promedio",
    markers=True,
    labels={"agno": "Año", "Promedio": "📝Puntaje"},
    title=f"Comparación Nacional vs SIMCE en {comuna}"
)

if not simce_comuna.empty:
    fig.add_scatter(
        x=simce_comuna["agno"], y=simce_comuna["Puntaje"],
        mode='lines+markers',
        name="SIMCE Comunal"
    )

st.plotly_chart(fig, use_container_width=True)

# COMPARACIÓN COMUNA VS REGIÓN VS NACIONAL 

st.markdown("### Comparación por Asignatura y Región")

# Obtener todas las comunas de la región seleccionada desde el diccionario
comunas_region = sum(regiones_interes[region].values(), [])

# Año más reciente con datos disponibles
ultimo_anio = simce_comuna["agno"].max() if not simce_comuna.empty else promedio["agno"].max()

# Filtrar SIMCE para comunas de la región seleccionada y año correspondiente
simce_region = simce[simce["comuna"].str.lower().isin([c.lower() for c in comunas_region])]
simce_region_anio = simce_region[simce_region["agno"] == ultimo_anio].copy()

# Selección de columna según asignatura
columna_puntaje = "lenguaje" if asignatura == "Lenguaje" else "matematicas"
if columna_puntaje in simce_region_anio.columns:
    simce_region_anio = simce_region_anio.rename(columns={columna_puntaje: "Puntaje"})
else:
    simce_region_anio["Puntaje"] = None

# Asegurarse de que Puntaje sea numérico y eliminar nulos
simce_region_anio["Puntaje"] = pd.to_numeric(simce_region_anio["Puntaje"], errors="coerce")
simce_region_anio = simce_region_anio.dropna(subset=["Puntaje"])

# Obtener promedio nacional del último año
try:
    promedio_nacional_val = promedio[promedio["agno"] == ultimo_anio][columna_puntaje].values[0]
except IndexError:
    promedio_nacional_val = None

# Obtener promedio regional y puntaje comunal
promedio_regional = simce_region_anio["Puntaje"].mean() if not simce_region_anio.empty else None
puntaje_comunal = simce_comuna[simce_comuna["agno"] == ultimo_anio]["Puntaje"].values[0] if not simce_comuna.empty else None

# Calcular mayor y menor puntaje de la región
if not simce_region_anio.empty:
    mayor_fila = simce_region_anio.loc[simce_region_anio["Puntaje"].idxmax()]
    menor_fila = simce_region_anio.loc[simce_region_anio["Puntaje"].idxmin()]
    mayor_puntaje = mayor_fila["Puntaje"]
    mayor_comuna = mayor_fila["comuna"]
    menor_puntaje = menor_fila["Puntaje"]
    menor_comuna = menor_fila["comuna"]
else:
    mayor_puntaje = menor_puntaje = None
    mayor_comuna = menor_comuna = "N/A"

# MÉTRICAS EN COLUMNAS

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(f"{comuna} - {asignatura} ({ultimo_anio})", f"{puntaje_comunal:.1f}" if puntaje_comunal else "N/A")

with col2:
    st.metric(f"Prom. Regional ({region})", f"{promedio_regional:.1f}" if promedio_regional else "N/A")

with col3:
    st.metric("Prom. Nacional", f"{promedio_nacional_val:.1f}" if promedio_nacional_val else "N/A")

col4, col5 = st.columns(2)
with col4:
    st.metric(f"🔼 Mayor Puntaje: {mayor_comuna}", f"{mayor_puntaje:.1f}" if mayor_puntaje else "N/A")
with col5:
    st.metric(f"🔽 Menor Puntaje: {menor_comuna}", f"{menor_puntaje:.1f}" if menor_puntaje else "N/A")

st.caption("📊 Comparación entre comuna seleccionada, su región y el país, por asignatura")

# MAYOR Y MENOR POR ASIGNATURA EN LA REGIÓN (METRICS VERTICALES) 

st.markdown(f"### 🏅 Mejor y Peor Puntaje de {region} ({ultimo_anio})")

# Filtrar SIMCE por región y año
comunas_region = sum(regiones_interes[region].values(), [])
simce_region = simce[simce["comuna"].str.lower().isin([c.lower() for c in comunas_region])]
simce_region_anio = simce_region[simce_region["agno"] == ultimo_anio].copy()

# Asegurar que las columnas sean numéricas
simce_region_anio["lenguaje"] = pd.to_numeric(simce_region_anio["lenguaje"], errors="coerce")
simce_region_anio["matematicas"] = pd.to_numeric(simce_region_anio["matematicas"], errors="coerce")

# Obtener datos válidos
lenguaje_data = simce_region_anio.dropna(subset=["lenguaje"])
matematicas_data = simce_region_anio.dropna(subset=["matematicas"])

# Inicializar resultados
mayor_lenguaje = menor_lenguaje = mayor_mate = menor_mate = "N/A"
mayor_lenguaje_val = menor_lenguaje_val = mayor_mate_val = menor_mate_val = None

# Lenguaje
if not lenguaje_data.empty:
    fila_max_lenguaje = lenguaje_data.loc[lenguaje_data["lenguaje"].idxmax()]
    fila_min_lenguaje = lenguaje_data.loc[lenguaje_data["lenguaje"].idxmin()]
    mayor_lenguaje = fila_max_lenguaje["comuna"]
    menor_lenguaje = fila_min_lenguaje["comuna"]
    mayor_lenguaje_val = fila_max_lenguaje["lenguaje"]
    menor_lenguaje_val = fila_min_lenguaje["lenguaje"]

# Matemáticas
if not matematicas_data.empty:
    fila_max_mate = matematicas_data.loc[matematicas_data["matematicas"].idxmax()]
    fila_min_mate = matematicas_data.loc[matematicas_data["matematicas"].idxmin()]
    mayor_mate = fila_max_mate["comuna"]
    menor_mate = fila_min_mate["comuna"]
    mayor_mate_val = fila_max_mate["matematicas"]
    menor_mate_val = fila_min_mate["matematicas"]

# Mostrar en 4 métricas verticales (una debajo de otra)
col1, col2 = st.columns(2)
col1.title("lenguaje")
col2.title("matematicas")

col1, col2, col3, col4 = st.columns(4)

col1.metric(label=f"Mayor puntaje:{mayor_lenguaje}", value=f"{mayor_lenguaje_val:.1f}" if mayor_lenguaje_val else "N/A") 
col2.metric(label=f" Menor puntaje:{menor_lenguaje}", value=f"{menor_lenguaje_val:.1f}" if menor_lenguaje_val else "N/A")
col3.metric(label=f" Mayor puntaje:{mayor_mate}", value=f"{mayor_mate_val:.1f}" if mayor_mate_val else "N/A")
col4.metric(label=f" Menor puntaje:{menor_mate}", value=f"{menor_mate_val:.1f}" if menor_mate_val else "N/A")

st.write("#### 📊 Mejores y peores puntajes por asignatura en comunas de la región seleccionada")
