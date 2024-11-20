#Comando de ejecución en un browser:           streamlit run ./proyectoABP.py
#Hospedar app en:    Streamlit Sharing, Heroku, o AWS.

import streamlit as st
import pandas as pd


#-----------------------------------------------------Carga de datos-----------------------------------------------
comics = pd.read_csv('./Marvel_Comics2.csv')#Cargar datos

#Cambiar nombre de las columnas
comics.columns = ['Nombre','AñosActivos','Titulo','FechaPublicacion',
                  'Descripcion','Dibujante','Escritor','DibujantePortada','Imprenta',
                  'Formato','Categoría','Precio']

#Quitar duplicados
comics.drop_duplicates(inplace=True)

#Gestion de valores NaN: Se pasan los valores nulos a una cadena vacía, se puede ver más adelante cuales compensan pasar a cadena vacía
comics['Nombre'].fillna('', inplace=True)
comics['AñosActivos'].fillna('', inplace=True)
comics['Titulo'].fillna('', inplace=True)
comics['FechaPublicacion'].fillna('', inplace=True)
comics['Descripcion'].fillna('', inplace=True)
comics['Dibujante'].fillna('', inplace=True)
comics['Escritor'].fillna('', inplace=True)
comics['DibujantePortada'].fillna('', inplace=True)
comics['Imprenta'].fillna('', inplace=True)
comics['Formato'].fillna('', inplace=True)
comics['Categoría'].fillna('', inplace=True)
comics['Precio'].fillna('', inplace=True)
#-------------------------------------------------------------------------------------------------------

#----------------------------------Variables globales-----------------------
columnas_simples = ['Titulo', 'Descripcion', 'Precio']
#---------------------------------------------------------------------------

#--------------------------Bloques css para estilos------------------------

st.markdown("""
    <style>
    .titulo {
        color: #7398c4;
        font-size: 50px;
        text-align: center;
        font-family: Arial, sans-serif;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <style>
    .texto {
        color: #a6bdbc;
        font-size: 20px;
        text-align: center;
        font-family: Arial, sans-serif;
    }
    </style>
""", unsafe_allow_html=True)

#--------------------------------------------------------------------------

#***************************************Funciones***************************************
def busqueda(cadena):
        
        fil = comics[comics['Titulo'].str.contains(cadena, case=False)]
        filtrado = fil[columnas_simples]
        # Mostrar el dataframe filtrado
        if not filtrado.empty:
            st.dataframe(filtrado, use_container_width=True)
        else:
            st.write("No se encontraron comics con ese término.")


#******************************************************************************************


st.markdown("<h1 class='titulo'>Sistema de recomendación de comics</h1>", unsafe_allow_html=True)

st.markdown("<h4 class='texto'>Buscar comics por nombre o título:</h4>", unsafe_allow_html=True)
search = st.text_input("")

if search:
    busqueda(search)
else:
    # Mostrar todos los comics si no hay texto de búsqueda
    st.dataframe(comics[columnas_simples], use_container_width=True)

