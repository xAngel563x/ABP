#Comando de ejecución en un browser:           streamlit run ./proyectoABP.py
#Hospedar app en:    Streamlit Sharing, Heroku, o AWS.

import streamlit as st
import pandas as pd
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import pairwise_distances



#-----------------------------------------------------Carga de datos-----------------------------------------------
def cargarComics():
    #Cargar datos
    comics = pd.read_csv('./Marvel_Comics2.csv')

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

    return comics

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

def crearTextoPreprocesado():
    nltk.download('punkt_tab')
    nltk.download('stopwords')

    ps = PorterStemmer()

    preprocessedText = []

    for row in comics.itertuples():


        text = word_tokenize(row[5]) ## indice de la columna que contiene el texto
        ## Remove stop words
        stops = set(stopwords.words("english"))
        text = [ps.stem(w) for w in text if not w in stops and w.isalnum()]
        text = " ".join(text)

        preprocessedText.append(text)

    comicsPreprocesado = comics
    comicsPreprocesado['TextoPreprocesado'] = preprocessedText

    return comicsPreprocesado

def vectorizarTexto(comicsPreprocesed):
    bolsaPalabras = TfidfVectorizer()
    bolsaPalabras.fit(comicsPreprocesed['TextoPreprocesado'])
    textosBoW= bolsaPalabras.transform(comicsPreprocesed['TextoPreprocesado'])
    return textosBoW

def crearMatrizDistancias(bolsa):
    matrizDistancias = pairwise_distances(bolsa,bolsa ,metric='cosine')
    return matrizDistancias

def instanciarMatrizDistancias():
    bolsa = vectorizarTexto(comicsPreprocesado)
    return crearMatrizDistancias(bolsa)

def busqueda(cadena,comic):
        
        fil = comic[comic['Titulo'].str.contains(cadena, case=False)]
        filtrado = fil[columnas_simples]
        # Mostrar el dataframe filtrado
        if not filtrado.empty:
            st.dataframe(filtrado, use_container_width=True)
        else:
            st.write("No se encontraron comics con ese término.")


def home():
    st.markdown("<h1 class='titulo'>Búsqueda de comics</h1>", unsafe_allow_html=True)

    st.markdown("<h4 class='texto'>Buscar comics por nombre o título:</h4>", unsafe_allow_html=True)
    search = st.text_input("")

    if search:
        busqueda(search, comics)
    else:
        # Mostrar todos los comics si no hay texto de búsqueda
        st.dataframe(comics[columnas_simples], use_container_width=True)


def sistema_recomendacion():
    st.markdown("<h1 class='titulo'>Bienvenido al sistema de recomendación:</h1>", unsafe_allow_html=True)

    st.markdown("<h4 class='texto'>Buscar comics por nombre o título:</h4>", unsafe_allow_html=True)
    search = st.text_input("", key="search")

    if search:
        busqueda(search, comicsPreprocesado)
    else:
        # Mostrar todos los comics si no hay texto de búsqueda
        st.dataframe(comicsPreprocesado[columnas_simples], use_container_width=True)

    st.markdown("<h4 class='texto'>Inserte titulo completo del comic:</h4>", unsafe_allow_html=True)

    titulo = st.text_input("", key="titulo")

    if titulo:
        indiceComic = comicsPreprocesado[comicsPreprocesado['Titulo']==titulo].index.values[0]

        distance_scores = list(enumerate(matrizDistancias[indiceComic]))#Se crea una lista con las distancias
        ordered_scores = sorted(distance_scores, key=lambda x: x[1])#Se ordenan las distancias
        top_scores = ordered_scores[1:11]#Se escojen las 10 mejores distancias
        top_indexes = [i[0] for i in top_scores]#Se buscan los indices de las peliculas con las 10 mejores distancias

        st.dataframe(comicsPreprocesado['Titulo'].iloc[top_indexes] , use_container_width=True)
    else:
        st.write("No se encontro el titulo")




def favoritos():
    st.markdown("<h1 class='titulo'>Bienvenido a tus favoritos:</h1>", unsafe_allow_html=True)

#******************************************************************************************

try:


    if "comics" not in st.session_state:
        st.session_state.comics = cargarComics()

    comics = st.session_state.comics
except:
    st.error("Error al cargar el archivo")



if "comicsPreprocesado" not in st.session_state:
    st.session_state.comicsPreprocesado = crearTextoPreprocesado()

comicsPreprocesado = st.session_state.comicsPreprocesado


if "matrizDistancias" not in st.session_state:
    st.session_state.matrizDistancias = instanciarMatrizDistancias()

matrizDistancias = st.session_state.matrizDistancias



menu = st.sidebar.radio(
        "",
        ["Home","Sistema de recomendación", "Favoritos"]
    )


if menu == "Home":
    home()
elif menu == "Sistema de recomendación":
    sistema_recomendacion()
elif menu == "Favoritos":
    favoritos()

