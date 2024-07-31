import streamlit as st
import pandas as pd
import plotly.express as px
import json
import geopandas as gpd
import folium
from streamlit_folium import st_folium

# Configuración de Streamlit
st.title("Visualización de Donaciones de Órganos")

# Funciones para cargar datos de donaciones y GeoJSON
@st.cache_data
def load_data():
    return pd.read_csv('donacion_organos.csv')

@st.cache_data
def load_geojson():
    try:
        with open('paises_del_mundo.geojson.json', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("El archivo 'paises_del_mundo.geojson.json' no se encuentra en el directorio.")
        return None
    except UnicodeDecodeError:
        st.error("Error al decodificar el archivo 'paises_del_mundo.geojson.json'. Asegúrate de que el archivo esté en UTF-8.")
        return None

# Cargar datos de donaciones
df_donaciones = load_data()
geojson_data = load_geojson()

if geojson_data is not None:
    # Asegúrate de que las columnas 'Donacion' y 'Cantidad' estén bien configuradas
    df_donaciones['Donacion'] = df_donaciones['Donacion'].fillna('No Especificado')
    df_donaciones['Cantidad'] = pd.to_numeric(df_donaciones['Cantidad'], errors='coerce').fillna(0)

    # Agregar un resumen para visualizar diferentes categorías
    df_summary = df_donaciones.groupby('Pais').agg({
        'Donacion': 'count',
        'Cantidad': 'sum'
    }).reset_index()

    # Renombrar las columnas para claridad
    df_summary.columns = ['Pais', 'Cantidad de Donaciones', 'Cantidad Total']

    # Verificar los nombres de los países en el GeoJSON
    features = geojson_data['features']
    names_geojson = [feature['properties'].get('etiqueta', 'Unknown') for feature in features]

    # Asegurarse de que el DataFrame tenga todos los países en el GeoJSON
    geojson_df = pd.DataFrame({
        'Pais': names_geojson
    })

    # Combinar con el DataFrame original
    df_summary = pd.merge(geojson_df, df_summary, on='Pais', how='left').fillna(0)

    # Crear el mapa de donaciones
    fig = px.choropleth(
        df_summary,
        geojson=geojson_data,
        locations='Pais',
        featureidkey='properties.etiqueta',  # Asegúrate de que esta clave sea correcta
        color='Cantidad Total',
        hover_name='Pais',
        hover_data={
            'Cantidad de Donaciones': True,
            'Cantidad Total': True
        },
        color_continuous_scale=px.colors.sequential.Plasma,
        scope='world',
        title='Mapa de Donaciones por País'
    )

    fig.update_layout(
        margin={"r":0,"t":0,"l":0,"b":0},
        geo=dict(showframe=False, showcoastlines=True, projection_type='equirectangular')
    )
    st.plotly_chart(fig)

    # Mostrar un resumen de las donaciones
    st.subheader('Resumen de Donaciones')
    st.dataframe(df_summary[['Pais', 'Cantidad de Donaciones', 'Cantidad Total']])

    # Crear un mapa de calor
    st.title('Mapa de Calor de Donaciones por País y Estado de Donación')

    fig_heatmap = px.density_heatmap(
        df_donaciones,
        x='Pais',
        y='Donacion',
        z='Cantidad',
        histfunc='sum',
        color_continuous_scale='Inferno',
        title='Mapa de Calor de Donaciones por País y Estado de Donación'
    )

    fig_heatmap.update_layout(
        xaxis_title='País',
        yaxis_title='Estado de Donación',
        margin={"r":0,"t":0,"l":0,"b":0}
    )
    st.plotly_chart(fig_heatmap)                                                                                                 

# Cargar datos de donaciones en Perú
excel_file = 'donacion_peru.xlsx'
donaciones_df = pd.read_excel(excel_file)

# Preprocesamiento de datos
donaciones_df['Cantidad'] = donaciones_df['Cantidad'].astype(int)
donaciones_df['Total Si Donan'] = donaciones_df.apply(lambda row: row['Cantidad'] if row['Donacion'] == 'Si acepta donar' else 0, axis=1)
donaciones_df['Total No Donan'] = donaciones_df.apply(lambda row: row['Cantidad'] if row['Donacion'] == 'No acepta donar' else 0, axis=1)

# Agrupar datos
agregado_departamentos = donaciones_df.groupby('Departamento').agg({
    'Total Si Donan': 'sum',
    'Total No Donan': 'sum',
    'Cantidad': 'sum'
}).reset_index()
agregado_departamentos['Total No Especificado'] = agregado_departamentos['Cantidad'] - (agregado_departamentos['Total Si Donan'] + agregado_departamentos['Total No Donan'])

agregado_provincias = donaciones_df.groupby('Provincia').agg({
    'Total Si Donan': 'sum',
    'Total No Donan': 'sum',
    'Cantidad': 'sum'
}).reset_index()
agregado_provincias['Total No Especificado'] = agregado_provincias['Cantidad'] - (agregado_provincias['Total Si Donan'] + agregado_provincias['Total No Donan'])

agregado_distritos = donaciones_df.groupby('Distrito').agg({
    'Total Si Donan': 'sum',
    'Total No Donan': 'sum',
    'Cantidad': 'sum'
}).reset_index()
agregado_distritos['Total No Especificado'] = agregado_distritos['Cantidad'] - (agregado_distritos['Total Si Donan'] + agregado_distritos['Total No Donan'])

# Selección del nivel administrativo
nivel = st.selectbox("Selecciona el nivel administrativo:", ["Departamentos", "Provincias", "Distritos"])

# Filtrado de datos
if nivel == "Departamentos":
    departamentos_lista = agregado_departamentos['Departamento'].unique().tolist()
    filtro_departamento = st.multiselect("Selecciona el Departamento:", departamentos_lista)
    if filtro_departamento:
        agregado_departamentos = agregado_departamentos[agregado_departamentos['Departamento'].isin(filtro_departamento)]
elif nivel == "Provincias":
    provincias_lista = agregado_provincias['Provincia'].unique().tolist()
    filtro_provincia = st.multiselect("Selecciona la Provincia:", provincias_lista)
    if filtro_provincia:
        agregado_provincias = agregado_provincias[agregado_provincias['Provincia'].isin(filtro_provincia)]
elif nivel == "Distritos":
    distritos_lista = agregado_distritos['Distrito'].unique().tolist()
    filtro_distrito = st.multiselect("Selecciona el Distrito:", distritos_lista)
    if filtro_distrito:
        agregado_distritos = agregado_distritos[agregado_distritos['Distrito'].isin(filtro_distrito)]

# Selección de sexo
sexo_lista = donaciones_df['Sexo'].unique().tolist()
filtro_sexo = st.multiselect("Selecciona el Sexo:", sexo_lista)
if filtro_sexo:
    donaciones_df = donaciones_df[donaciones_df['Sexo'].isin(filtro_sexo)]

# Selección de edades
edad_min = int(donaciones_df['Edad'].min())
edad_max = int(donaciones_df['Edad'].max())
filtro_edad = st.slider("Selecciona el rango de Edad:", edad_min, edad_max, (edad_min, edad_max))
filtro_edad_exacta = st.multiselect("Selecciona edades específicas:", range(edad_min, edad_max + 1))
if filtro_edad:
    donaciones_df = donaciones_df[(donaciones_df['Edad'] >= filtro_edad[0]) & (donaciones_df['Edad'] <= filtro_edad[1])]
if filtro_edad_exacta:
    donaciones_df = donaciones_df[donaciones_df['Edad'].isin(filtro_edad_exacta)]

# Mostrar resultados numéricos sin índice
st.write("Agregado por Departamento/Provincia/Distrito:")
if nivel == "Departamentos":
    st.dataframe(agregado_departamentos.style.hide(axis='index'))
elif nivel == "Provincias":
    st.dataframe(agregado_provincias.style.hide(axis='index'))
elif nivel == "Distritos":
    st.dataframe(agregado_distritos.style.hide(axis='index'))

# Cargar GeoJSON
departamentos = gpd.read_file('departamento.geojson')
provincias = gpd.read_file('provincia.geojson')
distritos = gpd.read_file('distrito.geojson')

# Ajustar nombres de columnas
departamentos = departamentos.rename(columns={'NOMBRE_DEP': 'departamento'})
provincias = provincias.rename(columns={'NOMBPROV': 'provincia'})
distritos = distritos.rename(columns={'NOMBDIST': 'distrito'})

# Fusionar datos
departamentos = departamentos.merge(agregado_departamentos, left_on='departamento', right_on='Departamento', how='left')
provincias = provincias.merge(agregado_provincias, left_on='provincia', right_on='Provincia', how='left')
distritos = distritos.merge(agregado_distritos, left_on='distrito', right_on='Distrito', how='left')

def crear_mapa(gdf, nombre_nivel):
    m = folium.Map(location=[-9.19, -75.015], zoom_start=6)

    # Añadir capa con área seleccionada
    selected = st.session_state.get('selected', None)

    def style_function(feature):
        color = 'blue'
        if selected and feature['properties'][nombre_nivel] == selected:
            color = 'red'
        return {
            'fillColor': color,
            'color': 'black',
            'weight': 2,
            'fillOpacity': 0.6  # Opacidad para el color
        }

    def highlight_function(feature):
        return {
            'weight': 3,
            'color': 'black',
            'fillOpacity': 0.4  # Opacidad menor al pasar el ratón sobre el elemento
        }

    folium.GeoJson(
        gdf.to_json(),
        name=f'{nombre_nivel} en el Mapa',
        style_function=style_function,
        highlight_function=highlight_function,
        tooltip=folium.GeoJsonTooltip(
            fields=[nombre_nivel],
            aliases=[nombre_nivel.capitalize()],
            localize=True
        )
    ).add_to(m)
    
    folium.LayerControl().add_to(m)
    
    return m

# Crear y mostrar el mapa
if nivel == "Departamentos":
    st.write("Mapa de Departamentos")
    m = crear_mapa(departamentos, 'departamento')
    st_folium(m, width=700, height=500)
    selected_departamento = st.selectbox("Selecciona un Departamento para resaltar:", departamentos['departamento'].unique())
    st.session_state['selected'] = selected_departamento

elif nivel == "Provincias":
    st.write("Mapa de Provincias")
    m = crear_mapa(provincias, 'provincia')
    st_folium(m, width=700, height=500)
    selected_provincia = st.selectbox("Selecciona una Provincia para resaltar:", provincias['provincia'].unique())
    st.session_state['selected'] = selected_provincia

elif nivel == "Distritos":
    st.write("Mapa de Distritos")
    m = crear_mapa(distritos, 'distrito')
    st_folium(m, width=700, height=500)
    selected_distrito = st.selectbox("Selecciona un Distrito para resaltar:", distritos['distrito'].unique())
    st.session_state['selected'] = selected_distrito

# Panel de información
if 'selected' in st.session_state:
    selected = st.session_state['selected']
    if nivel == "Departamentos":
        info = agregado_departamentos[agregado_departamentos['Departamento'] == selected]
    elif nivel == "Provincias":
        info = agregado_provincias[agregado_provincias['Provincia'] == selected]
    elif nivel == "Distritos":
        info = agregado_distritos[agregado_distritos['Distrito'] == selected]
    
    st.write("### Información del Seleccionado")
    st.write(info)