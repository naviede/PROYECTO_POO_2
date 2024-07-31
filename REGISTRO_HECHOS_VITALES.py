import os
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import plotly.io as pio
import imageio
import numpy as np

# Ajusta la ruta del archivo Excel aquí
file_path = 'C:/PROYECTO_POO_2/registro de hechos vitales de las personas_nacimientos_matrimonios_defunciones.xlsx'

# Verificar si el archivo existe
if not os.path.exists(file_path):
    raise FileNotFoundError(f"No se encontró el archivo en la ruta especificada: {file_path}")

# Cargar el archivo Excel
data = pd.read_excel(file_path, sheet_name='17_OPP_2024_Mar_0')

# Filtrar datos para las columnas y años relevantes
data_filtered = data[(data['AÑO_INSCRIPCION'] >= 2012)][['AÑO_INSCRIPCION', 'COD_HECHO', 'CANTIDAD']]

# Pivotar los datos para obtener las cuentas por año para cada evento
data_pivot = data_filtered.pivot_table(index='AÑO_INSCRIPCION', columns='COD_HECHO', values='CANTIDAD', aggfunc='sum', fill_value=0)

# Crear el gráfico de barras 3D
fig = go.Figure()

years = data_pivot.index
events = data_pivot.columns

for event in events:
    fig.add_trace(go.Scatter3d(
        x=years,
        y=[event] * len(years),
        z=data_pivot[event],
        mode='markers+lines',
        marker=dict(size=8),
        line=dict(width=5),
        name=event
    ))

# Actualizar el diseño para mejor visualización
fig.update_layout(
    title='Nacimientos, Matrimonios y Defunciones en Perú (2012-2024)',
    scene=dict(
        xaxis_title='Año',
        yaxis_title='Hecho Vital',
        zaxis_title='Cantidad',
        yaxis=dict(tickvals=[0, 1, 2], ticktext=events)
    ),
    width=800,
    height=600,
)

# Mostrar el gráfico en Streamlit
st.title('Visualización 3D de Hechos Vitales en Perú')
st.plotly_chart(fig)

# Exportar el gráfico como un video
pio.write_image(fig, 'plot.png', format='png')

# Crear una lista de cuadros
frames = []

# Crear cuadros de video girando el gráfico
for angle in range(0, 360, 10):
    fig.update_layout(scene_camera=dict(eye=dict(x=1.5*np.cos(np.radians(angle)), y=1.5*np.sin(np.radians(angle)), z=1)))
    image_path = f"plot_{angle}.png"
    pio.write_image(fig, image_path, format='png')
    frames.append(imageio.imread(image_path))

# Guardar los cuadros como un video
video_path = 'plot_video.mp4'
imageio.mimsave(video_path, frames, fps=10)

print("Video guardado en:", video_path)

import pandas as pd
import plotly.graph_objs as go
import streamlit as st

# Ruta del archivo Excel
file_path = 'registro de hechos vitales de las personas_nacimientos_matrimonios_defunciones.xlsx'

# Cargar el archivo Excel
data = pd.read_excel(file_path, sheet_name='17_OPP_2024_Mar_0')

# Renombrar columnas para mayor claridad
data.rename(columns={'DEPA_CONT_L': 'DEPARTAMENTO', 'PROV_PAIS_L': 'PROVINCIA', 'DIST_CIUD_L': 'DISTRITO'}, inplace=True)

# Filtrar datos hasta 2023
data = data[data['AÑO_INSCRIPCION'] <= 2023]

# Agrupar los datos por año, departamento y tipo de hecho
data_grouped = data.groupby(['AÑO_INSCRIPCION', 'DEPARTAMENTO', 'COD_HECHO'])['CANTIDAD'].sum().reset_index()

# Filtrar por tipo de hecho
nacimientos = data_grouped[data_grouped['COD_HECHO'] == 'Nacimiento']
matrimonios = data_grouped[data_grouped['COD_HECHO'] == 'Matrimonio']
defunciones = data_grouped[data_grouped['COD_HECHO'] == 'Defunción']

# Crear gráficos de barras 3D
def create_animated_3d_bar_chart(data, title):
    frames = []
    departments = data['DEPARTAMENTO'].unique()
    years = sorted(data['AÑO_INSCRIPCION'].unique())
    
    for year in years:
        yearly_data = data[data['AÑO_INSCRIPCION'] == year]
        frame = go.Frame(data=[go.Bar(
            x=yearly_data['DEPARTAMENTO'],
            y=yearly_data['CANTIDAD'],
            marker=dict(color=yearly_data['CANTIDAD'], colorscale='Viridis'),
        )], name=str(year))
        frames.append(frame)
    
    fig = go.Figure(
        data=[go.Bar(
            x=departments,
            y=data[data['AÑO_INSCRIPCION'] == years[0]]['CANTIDAD'],
            marker=dict(color=data[data['AÑO_INSCRIPCION'] == years[0]]['CANTIDAD'], colorscale='Viridis'),
        )],
        layout=go.Layout(
            title=title,
            xaxis=dict(title='Departamento'),
            yaxis=dict(title='Cantidad'),
            updatemenus=[dict(
                type='buttons',
                showactive=False,
                buttons=[dict(label='Play',
                              method='animate',
                              args=[None, dict(frame=dict(duration=1000, redraw=True), fromcurrent=True)])]
            )],
            sliders=[dict(
                steps=[dict(method='animate', args=[[str(year)], dict(mode='immediate', frame=dict(duration=1000, redraw=True))], label=str(year)) for year in years],
                transition={'duration': 1000},
                x=0.1,
                xanchor='left',
                y=-0.1,
                yanchor='top'
            )]
        ),
        frames=frames
    )
    
    return fig

fig_nacimientos = create_animated_3d_bar_chart(nacimientos, 'Nacimientos por Departamento y Año')
fig_matrimonios = create_animated_3d_bar_chart(matrimonios, 'Matrimonios por Departamento y Año')
fig_defunciones = create_animated_3d_bar_chart(defunciones, 'Defunciones por Departamento y Año')

# Análisis e interpretación
def get_analysis(data, event_type):
    min_event = data.loc[data['CANTIDAD'].idxmin()]
    max_event = data.loc[data['CANTIDAD'].idxmax()]
    total_by_department = data.groupby('DEPARTAMENTO')['CANTIDAD'].sum()
    trend = total_by_department.pct_change().fillna(0) * 100
    most_development = trend.idxmax()

    analysis = f"Análisis de {event_type}:\n\n"
    analysis += f"- El departamento con menos {event_type} es {min_event['DEPARTAMENTO']} en el año {min_event['AÑO_INSCRIPCION']} con {min_event['CANTIDAD']}.\n"
    analysis += f"- El departamento con más {event_type} es {max_event['DEPARTAMENTO']} en el año {max_event['AÑO_INSCRIPCION']} con {max_event['CANTIDAD']}.\n"
    analysis += f"- El departamento con mayor desarrollo en {event_type} es {most_development} con un cambio del {trend[most_development]:.2f}%.\n"
    
    return analysis

analysis_nacimientos = get_analysis(nacimientos, 'nacimientos')
analysis_matrimonios = get_analysis(matrimonios, 'matrimonios')
analysis_defunciones = get_analysis(defunciones, 'defunciones')

# Crear la interfaz de Streamlit
st.title('Visualización de Hechos Vitales en Perú por Nivel Administrativo y Año')

st.header('Nacimientos')
st.plotly_chart(fig_nacimientos)
st.markdown(f"<p style='color: #ffffff;'>{analysis_nacimientos}</p>", unsafe_allow_html=True)

st.header('Matrimonios')
st.plotly_chart(fig_matrimonios)
st.markdown(f"<p style='color: #ffffff;'>{analysis_matrimonios}</p>", unsafe_allow_html=True)

st.header('Defunciones')
st.plotly_chart(fig_defunciones)
st.markdown(f"<p style='color: #ffffff;'>{analysis_defunciones}</p>", unsafe_allow_html=True)