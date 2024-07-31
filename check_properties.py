import pandas as pd

# Carga el archivo CSV
donaciones_df = pd.read_csv('C:/PROYECTO_POO_2/donacion_peru.csv')

# Eliminar columnas duplicadas
donaciones_df = donaciones_df.loc[:, ~donaciones_df.columns.duplicated()]

# Verifica que las columnas duplicadas hayan sido eliminadas
print("Columnas en donaciones_df después de eliminar duplicados:", donaciones_df.columns)
