import numpy as np
import pandas as pd
from sklearn import datasets
from sklearn.cluster import KMeans
from sklearn.metrics import pairwise_distances_argmin_min
from sklearn.metrics import silhouette_samples, silhouette_score
from datetime import datetime
from django.http import JsonResponse
from django.conf import settings
import os


def kmeans_prueba(request):

    parametro1 = request.GET.get('parametro1')
    parametro2 = request.GET.get('parametro2')

    mensaje = f"Estoy funcionando con {parametro1} y {parametro2}"
    print("Estoy funcionando")

    response_data = {'mensaje': mensaje}
    return JsonResponse(response_data)

def kmeans_criticidad(request):

    mensaje="Estoy funcionando"
    print("Estoy funcionando")

    #CARGA DE LA BDD
    url = os.path.join(settings.STATICFILES_DIRS[0], 'app', 'recursos', 'csv', 'bdd_pacientes.csv')
    df = pd.read_csv(url, index_col=None)

    #CREACIÓN DEL DF CON LAS VARIABLES IMPORTANTES

    df2 = pd.DataFrame()
    lista = []
    for i in range(0,110527):
        lista.append(i)
    df2.insert(0, 'id', lista)
    df2.insert(1, 'edad', df.loc[:,'Age'])
    df2.insert(2, 'hipertension', df.loc[:,'Hipertension'])
    df2.insert(3, 'diabetes', df.loc[:,'Diabetes'])

    #print(df2)

    #LIMPIEZA DE DATOS

    null_counts = df2.isnull().sum()

    total_registros = len(df2)
    porcentaje_nulos = (null_counts / total_registros) * 100

    print("Total de nulos registrados por columna:")
    print(null_counts)
    print("\nPorcentaje de nulos registrados por columna:")
    print(porcentaje_nulos)

    #ELIMINACIÓN DE OUTLAYERS

    df_final = df2[(df2['edad'] < -1) | (df2['edad'] > 10)]

    frecuencia_edades = df_final['edad'].value_counts()

    # Encuentra la edad que más se repite
    edad_mas_comun = frecuencia_edades.idxmax()

    # Imprime la edad que más se repite y su frecuencia
    #print(f"La edad más común es {edad_mas_comun} con {frecuencia_edades.max()} ocurrencias.")

    print(df_final)

    #CREACIÓN DE FILTROS

    datos2 = df_final

    datos2['criticidad_vocal'] = 0

    # Filtro: 
    filtro_edad_mayor_75 = (datos2['edad'] > 75) & ((datos2['hipertension'] == 1) | (datos2['diabetes'] == 1))
    datos2.loc[filtro_edad_mayor_75, 'criticidad_vocal'] = 3  # Alta probabilidad

    filtro_edad_hipertension_diabetes = (datos2['edad'].between(60, 75)) & (datos2['hipertension'] == 1) & (datos2['diabetes'] == 1)
    datos2.loc[filtro_edad_hipertension_diabetes, 'criticidad_vocal'] = 3  # Alta probabilidad

    filtro_edad_65_o_mas = (datos2['edad'] >= 65)
    datos2.loc[filtro_edad_65_o_mas, 'criticidad_vocal'] = 3  # Alta probabilidad

    filtro_edad_hipertension = (datos2['edad'].between(45, 64)) & (datos2['hipertension'] == 1)
    datos2.loc[filtro_edad_hipertension, 'criticidad_vocal'] = 2  # Moderada probabilidad

    filtro_edad_hipertension_sin_diabetes = (datos2['edad'].between(30, 45)) & (datos2['hipertension'] == 1) & (datos2['diabetes'] == 0)
    datos2.loc[filtro_edad_hipertension_sin_diabetes, 'criticidad_vocal'] = 2  # Moderada probabilidad

    filtro_edad_hipertension_severa = (datos2['edad'] > 50) & (datos2['hipertension'].isin([2, 3]))  # Suponiendo que 2 es moderada y 3 es severa
    datos2.loc[filtro_edad_hipertension_severa, 'criticidad_vocal'] = 3  # Alta probabilidad

    filtro_hipertension_diabetes = (datos2['hipertension'] == 1) & (datos2['diabetes'] == 1)
    datos2.loc[filtro_hipertension_diabetes, 'criticidad_vocal'] = 3  # Alta probabilidad

    filtro_edad_diabetes = (datos2['edad'].between(40, 59)) & (datos2['diabetes'] == 1)
    datos2.loc[filtro_edad_diabetes, 'criticidad_vocal'] = 2  # Moderada probabilidad

    filtro_edad_menor_18 = (datos2['edad'] < 18) & ((datos2['hipertension'] == 1) | (datos2['diabetes'] == 1))
    datos2.loc[filtro_edad_menor_18, 'criticidad_vocal'] = 1  # Baja probabilidad

    filtro_edad_menor_30_sin_condiciones = (datos2['edad'] < 30) & (datos2['hipertension'] == 0) & (datos2['diabetes'] == 0)
    datos2.loc[filtro_edad_menor_30_sin_condiciones, 'criticidad_vocal'] = 1  # Baja probabilidad

    filtro_edad_menor_64 = (datos2['edad'] <= 64)
    datos2.loc[filtro_edad_menor_64, 'criticidad_vocal'] = 2  # Moderada probabilidad

    filtro_edad_menor_35 = (datos2['edad'] <= 35)
    datos2.loc[filtro_edad_menor_35, 'criticidad_vocal'] = 1  # Baja probabilidad

    filtro_edad_diabetes = (datos2['edad'].between(55, 64)) & ((datos2['hipertension'] == 1) | (datos2['diabetes'] == 1))
    datos2.loc[filtro_edad_diabetes, 'criticidad_vocal'] = 3  # Moderada probabilidad

    datos2['criticidad_vocal'].astype(int)

    #CREACION DEL KMEANS

    df2 = datos2

    #Para el ejercicio, sólo seleccionamos 3 dimensiones, para poder graficarlo
    X = np.array(df2[['edad','hipertension','diabetes']])
    y = np.array(df2.astype(int)['criticidad_vocal'])
    X.shape

    #ENTRENAMIENTO DEL KMEANS

    # Instantiate the KMeans models
    km = KMeans(n_clusters=3, random_state=42)

    # Fit the KMeans model
    km.fit_predict(X)

    # Calculate Silhoutte Score 
    # print("cargando score . . .")
    # score = silhouette_score(X, km.labels_, metric='euclidean')
    # scoreRound = round(score, 1)

    # Print the score
    # print('Silhouetter Score: %.3f' % scoreRound)
    # Silhouetter Score: 0.600

    #ANALIZAR
    #3 valor K, ETIQUETAS Y CENTROIDES

    kmeans = KMeans(n_clusters=3).fit(X)
    centroids = kmeans.cluster_centers_
    print(centroids)

    # Obtenemos las etiquetas de cada punto de nuestros datos
    labels = kmeans.predict(X)
    # Obtenemos los centroids
    C = kmeans.cluster_centers_
    colores=['red','green','blue']
    asignar=[]
    for row in labels:
        asignar.append(colores[row])


    #USUARIOS POR CLUSTER
    copy =  pd.DataFrame()
    copy['id']= df2['id'].values
    copy['criticidad_vocal']=df2['criticidad_vocal'].values
    copy['label'] = labels
    cantidadGrupo =  pd.DataFrame()
    cantidadGrupo['color']=colores
    cantidadGrupo['cantidad']=copy.groupby('label').size()
    print(cantidadGrupo)

    #VARIABLES DEL USUARIO

    edad = int(request.GET.get('edad_paciente'))
    diabetes_paciente = int(request.GET.get('diabetes_paciente'))
    hipertension_paciente = int(request.GET.get('hipertension_paciente'))

    print(edad)

    if diabetes_paciente <= 6:
        print("Tiene diabetes")
        diabetes_pa = 1
    else:
        diabetes_pa = 0

    if hipertension_paciente <= 2:
        print("Tiene hipertension")
        hipertension_paciente = 1
    else:
        hipertension_paciente = 0

    #SE REALIZA LAS PREDICCIONES

    X_new = np.array([[edad,diabetes_pa,hipertension_paciente]])
    new_labels = kmeans.predict(X_new)
    print(new_labels)

    print(edad) 

    prediccion = int(new_labels[0])

    if prediccion == 1:
        prediccion = "Baja probabilidad"
    elif prediccion == 0:
        prediccion = "Mediana probabilidad"
    else:
        prediccion = "Alta probabilidad"

    response_data = {'prediccion': prediccion}
    return JsonResponse(response_data)