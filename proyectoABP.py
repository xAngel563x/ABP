#Comando de ejecución en un browser:           streamlit run ./proyectoABP.py
#Hospedar app en:    Streamlit Sharing, Heroku, o AWS.

import streamlit as st
import pandas as pd
import nltk
import os
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import pairwise_distances
from sklearn import svm



#------------------------------------------------Carga de datos-----------------------------------------------
def cargarComics():
    #Cargar datos
    comics = pd.read_csv('./marvel-test3.csv')

    #Cambiar nombre de las columnas
    comics.columns = ['Indice','Nombre','AñosActivos','Titulo','FechaPublicacion',
                  'Descripcion','Dibujante','Escritor','DibujantePortada','Imprenta',
                  'Formato','Categoría','Precio','label','text']

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
columnas_simples = ["Titulo","Descripcion","FechaPublicacion","AñosActivos","Escritor","Dibujante","Precio"]
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

#Estilo del footer
st.markdown(
    """
    <style>
    .footer {
        position: fixed;
        bottom: 0;
        right: 0;
        color: grey;
        font-size: 12px;
        padding: 10px;
    }
    </style>
    <div class="footer">
        © 2024 - Proyecto de ABP
    </div>
    """,
    unsafe_allow_html=True
)

# CSS personalizado para la barra lateral
st.markdown(
    """
    <style>
    [data-testid="stSidebar"] {
        background-color: #007786;
        padding: 20px;
        border-right: 3px solid #48cae4;
    }
    </style>
    """,
    unsafe_allow_html=True
)

#--------------------------------------------------------------------------

#***************************************Funciones***************************************

def crearTextoPreprocesado():
    nltk.download('punkt_tab')
    nltk.download('stopwords')

    ps = PorterStemmer()

    preprocessedText = []

    for row in comics.itertuples():

        
        text = word_tokenize(row[6]) ## indice de la columna que contiene el texto
        ## Remove stop words
        stops = set(stopwords.words("english"))
        text = [ps.stem(w) for w in text if not w in stops and w.isalnum()]
        text = " ".join(text)

        preprocessedText.append(text)
        

    comicsPreprocesado = comics
    comicsPreprocesado['SinopsisPreprocesado'] = preprocessedText

    return comicsPreprocesado

def cargarBolsaSentimientos():
    trainingData = pd.read_csv('./marvel-train.csv')
    ps = PorterStemmer()

    textoProcesado = []

    for row in trainingData.itertuples():


        text = word_tokenize(row.body) ## indice de la columna que contiene el texto
        ## Remove stop words
        stops = set(stopwords.words("english"))
        text = [ps.stem(w) for w in text if not w in stops and w.isalnum()]
        text = " ".join(text)

        textoProcesado.append(text)

    datosProcesados = trainingData
    datosProcesados['ReviewPreprocesada'] = textoProcesado

    #Se carga la bolsa de palabras para las reviews
    bolsaSentimientos = TfidfVectorizer()
    bolsaSentimientos.fit(datosProcesados['ReviewPreprocesada'])    
    return bolsaSentimientos

def cargarModelo():
    trainingData = pd.read_csv('./marvel-train.csv')

    #Se preprocesan las reviews
    nltk.download('punkt_tab')
    nltk.download('punkt')
    nltk.download('stopwords')


    print(os.path.exists(nltk.data.find('tokenizers/punkt')))

    ps = PorterStemmer()

    textoProcesado = []

    for row in trainingData.itertuples():


        text = word_tokenize(row.body) ## indice de la columna que contiene el texto
        ## Remove stop words
        stops = set(stopwords.words("english"))
        text = [ps.stem(w) for w in text if not w in stops and w.isalnum()]
        text = " ".join(text)

        textoProcesado.append(text)

    datosProcesados = trainingData
    datosProcesados['ReviewPreprocesada'] = textoProcesado

    #Se carga la bolsa de palabras para las reviews
    bolsaSentimientos = TfidfVectorizer()
    bolsaSentimientos.fit(datosProcesados['ReviewPreprocesada'])    
    textsBoW= bolsaSentimientos.transform(datosProcesados['ReviewPreprocesada'])

    #Se entrena el algoritmo
    svc = svm.SVC(kernel='linear') #Modelo de clasificación

    X_train = textsBoW #Documentos
    Y_train = trainingData['label'] #Etiquetas de los documentos
    svc.fit(X_train, Y_train) #Entrenamiento

    return svc

def vectorizarTexto(comicsPreprocesed):
    bolsaPalabras = TfidfVectorizer()
    bolsaPalabras.fit(comicsPreprocesed['SinopsisPreprocesado'])
    textosBoW= bolsaPalabras.transform(comicsPreprocesed['SinopsisPreprocesado'])
    return textosBoW

def crearMatrizDistancias(bolsa):
    matrizDistancias = pairwise_distances(bolsa,bolsa ,metric='cosine')
    return matrizDistancias

def instanciarMatrizDistancias():
    bolsa = vectorizarTexto(comicsPreprocesado)
    return crearMatrizDistancias(bolsa)

def busqueda(cadena,comic):
        
        filtrado = comic[comic['Titulo'].str.contains(cadena, case=False)]
        
        # Mostrar el dataframe filtrado
        if not filtrado.empty:
            st.dataframe(filtrado[columnas_simples], use_container_width=True)
        else:
            st.write("No se encontraron comics con ese término.")

def busquedaTit(cadena,comic):
        
        filtrado = comic[comic['Titulo'].str.contains(cadena, case=False)]
        
        # Mostrar el dataframe filtrado
        if not filtrado.empty:
            st.dataframe(filtrado, use_container_width=True)
        else:
            st.write("No se encontraron comics con ese término.")
def busquedaReview(cadena,comic):
    filtrado = comic[comic['Titulo'].str.contains(cadena, case=False)]
        
    # Mostrar el dataframe filtrado
    if not filtrado.empty:
        st.dataframe(filtrado[["Titulo","text","label"]], use_container_width=True)
    else:
        st.write("No se encontraron comics con ese término.")


def home():
    st.markdown("<h1 class='titulo'>BuscaComics</h1>", unsafe_allow_html=True)

    st.markdown("<h4 class='texto'>Buscar información de comics por título:</h4>", unsafe_allow_html=True)
    search = st.text_input("")

    if search:
        busqueda(search, comics)
    else:
        # Mostrar todos los comics si no hay texto de búsqueda
        st.dataframe(comics[columnas_simples], use_container_width=True)


def sistema_recomendacion():
    st.markdown("<h1 class='titulo'>Bienvenido al sistema de recomendación:</h1>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<h4 class='texto'>Buscar comics por título:</h4>", unsafe_allow_html=True)
        search = st.text_input("", key="search")
        if search:
            fil = comicsPreprocesado[["Titulo"]]
            busquedaTit(search, fil)
        else:
            # Mostrar todos los comics si no hay texto de búsqueda
            st.dataframe(comicsPreprocesado[["Titulo"]], use_container_width=True)



    with col2:
        st.markdown("<h4 class='texto'>Titulo completo del comic:</h4>", unsafe_allow_html=True)
        titulo = st.text_input("", key="titulo")
        if titulo:
            try:
                indiceComic = comicsPreprocesado[comicsPreprocesado['Titulo']==titulo].index.values[0]

                distance_scores = list(enumerate(matrizDistancias[indiceComic]))#Se crea una lista con las distancias
                ordered_scores = sorted(distance_scores, key=lambda x: x[1])#Se ordenan las distancias
                top_scores = ordered_scores[1:11]#Se escojen las 10 mejores distancias
                top_indexes = [i[0] for i in top_scores]#Se buscan los indices de las peliculas con las 10 mejores distancias

                st.markdown("<p class='texto'>Comics recomendados:</p>", unsafe_allow_html=True)
                st.dataframe(comicsPreprocesado['Titulo'].iloc[top_indexes] , use_container_width=True)
            except:
                st.write("El titulo no se encuentra en la base de datos")
        else:
            st.write("No se encontro el titulo")




def favoritos():
    st.markdown("<h1 class='titulo'>Bienvenido a tus favoritos:</h1>", unsafe_allow_html=True)
    st.markdown("<h4 class='texto'>Proximamente...</h4>", unsafe_allow_html=True)

def tusReviews():
    st.markdown("<h1 class='titulo'>Bienvenido a tus reviews:</h1>", unsafe_allow_html=True)
    seleccionado = ""

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<h4 class='texto'>Buscar comics por título:</h4>", unsafe_allow_html=True)
        search = st.text_input("", key="search")
        if search:
            fil = comicsPreprocesado[["Titulo","text"]]
            busquedaTit(search, fil)
        else:
            # Mostrar todos los comics si no hay texto de búsqueda
            st.dataframe(comicsPreprocesado[["Titulo","text"]], use_container_width=True)



    with col2:
        st.markdown("<h4 class='texto'>Titulo completo del comic al que deseas ponerle una review:</h4>", unsafe_allow_html=True)
        titulo = st.text_input("", key="titulo")
        if titulo:
            try:

                st.dataframe(comicsPreprocesado[comicsPreprocesado['Titulo'] == titulo][["Titulo","text","label"]] , use_container_width=True)
            except:
                st.write("El titulo no se encuentra en la base de datos")
        else:
            st.write("No se encontro el titulo")

    if titulo != "":
        st.markdown("<h4 class='texto'>Comentario a escribir:</h4>", unsafe_allow_html=True)
        coment = st.text_input("", key="coment")
        if coment:
            botonSubir = st.button("Subir")
            if botonSubir and coment != "":

                ps = PorterStemmer()

                text = word_tokenize(coment)
                stops = set(stopwords.words("english"))
                text = [ps.stem(w) for w in text if not w in stops and w.isalnum()]
                text = " ".join(text)

                comicsPreprocesado.loc[comicsPreprocesado['Titulo'] == titulo, 'text'] = coment

                nuevaReviewVectorizada = bolsaSentimientos.transform([text])
                prediccion = modelo.predict(nuevaReviewVectorizada)

                comicsPreprocesado.loc[comicsPreprocesado['Titulo'] == titulo, 'label'] = prediccion

                if prediccion == 1:
                    st.write("Tu review ha sido catalogada como positiva")
                if prediccion == 0:
                    st.write("Tu review ha sido catalogada como neutral")
                if prediccion == -1:
                    st.write("Tu review ha sido catalogada como negativa")


        else:
            st.write("No se ha seleccionado ningun titulo")



def paraLeer():
    st.markdown("<h1 class='titulo'>Bienvenido a tus comics para leer:</h1>", unsafe_allow_html=True)
    st.markdown("<h4 class='texto'>Proximamente...</h4>", unsafe_allow_html=True)

def reviews():
    st.markdown("<h1 class='titulo'>Bienvenido a las reviews públicas</h1>", unsafe_allow_html=True)

    st.markdown("<h4 class='texto'>Buscar reviews de comics por título:</h4>", unsafe_allow_html=True)
    search = st.text_input("",key="search")

    if search:
        busquedaReview(search,comics)
    else:
        # Mostrar todos los comics si no hay texto de búsqueda
        st.dataframe(comics[["Titulo","text","label"]], use_container_width=True)
    
    titulo = st.text_input("",key="titulo")

    if titulo:
        st.dataframe(comicsPreprocesado[comicsPreprocesado['Titulo'] == titulo][["Titulo","text","label"]] , use_container_width=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            botonLike = st.button("Like", key="botonLike")
        with col2:
            botonNeutro = st.button("Normal", key="botonNeutro")
        with col3:
            botonDislike = st.button("Dislike", key="botonDislike")
        if botonLike:
            comicsPreprocesado.loc[comicsPreprocesado['Titulo'] == titulo, 'label'] = 1
        if botonNeutro:
            comicsPreprocesado.loc[comicsPreprocesado['Titulo'] == titulo, 'label'] = 0
        if botonDislike:
            comicsPreprocesado.loc[comicsPreprocesado['Titulo'] == titulo, 'label'] = -1
    else:
        st.write("El titulo no esta en la base de datos")



#******************************************************************************************


if "comics" not in st.session_state:
    st.session_state.comics = cargarComics()

comics = st.session_state.comics


if "comicsPreprocesado" not in st.session_state:
    st.session_state.comicsPreprocesado = crearTextoPreprocesado()

comicsPreprocesado = st.session_state.comicsPreprocesado


if "matrizDistancias" not in st.session_state:
    st.session_state.matrizDistancias = instanciarMatrizDistancias()

matrizDistancias = st.session_state.matrizDistancias


if "modelo" not in st.session_state:
    st.session_state.modelo = cargarModelo()

modelo = st.session_state.modelo

if "bolsaSentimientos" not in st.session_state:
    st.session_state.bolsaSentimientos = cargarBolsaSentimientos()

bolsaSentimientos = st.session_state.bolsaSentimientos

st.sidebar.title("Opciones")

menu = st.sidebar.radio(
        "",
        ["Home","Sistema de recomendación", "Comics para leer", "Favoritos", "Tus reviews", "Reviews públicas"]
    )


if menu == "Home":
    home()
elif menu == "Sistema de recomendación":
    sistema_recomendacion()
elif menu == "Favoritos":
    favoritos()
elif menu == "Tus reviews":
    tusReviews()
elif menu == "Comics para leer":
    paraLeer()
elif menu == "Reviews públicas":
    reviews()

