import streamlit as st
from pytube import YouTube, Playlist
import os
from moviepy.editor import VideoFileClip
import time
from pytube.innertube import _default_clients
from pytube import cipher
import re

# Ajustes de pytube para evitar problemas con la versión de cliente
_default_clients["ANDROID"]["context"]["client"]["clientVersion"] = "19.08.35"
_default_clients["IOS"]["context"]["client"]["clientVersion"] = "19.08.35"
_default_clients["ANDROID_EMBED"]["context"]["client"]["clientVersion"] = "19.08.35"
_default_clients["IOS_EMBED"]["context"]["client"]["clientVersion"] = "19.08.35"
_default_clients["IOS_MUSIC"]["context"]["client"]["clientVersion"] = "6.41"
_default_clients["ANDROID_MUSIC"] = _default_clients["ANDROID_CREATOR"]

def get_throttling_function_name(js: str) -> str:
    function_patterns = [
        r'a\.[a-zA-Z]\s*&&\s*\([a-z]\s*=\s*a\.get\("n"\)\)\s*&&\s*'
        r'\([a-z]\s*=\s*([a-zA-Z0-9$]+)(\[\d+\])?\([a-z]\)',
        r'\([a-z]\s*=\s*([a-zA-Z0-9$]+)(\[\d+\])\([a-z]\)',
    ]
    for pattern in function_patterns:
        regex = re.compile(pattern)
        function_match = regex.search(js)
        if function_match:
            if len(function_match.groups()) == 1:
                return function_match.group(1)
            idx = function_match.group(2)
            if idx:
                idx = idx.strip("[]")
                array = re.search(
                    r'var {nfunc}\s*=\s*(\[.+?\]);'.format(
                        nfunc=re.escape(function_match.group(1))),
                    js
                )
                if array:
                    array = array.group(1).strip("[]").split(",")
                    array = [x.strip() for x in array]
                    return array[int(idx)]
    raise Exception(
        caller="get_throttling_function_name", pattern="multiple"
    )

cipher.get_throttling_function_name = get_throttling_function_name

def ListaDeReproduccion(link, Comenzar):
    CancionActual = Comenzar
    yt = Playlist(link)
    st.write(f'Descargando: {yt.title}')
    for i, video in enumerate(yt.videos):
        if i >= CancionActual:
            try:
                st.write(f"Name: {video.title} No. canción: {i}")
                Descarga = video.streams.filter(progressive=True, file_extension="mp4").first()
                downloaded_file = Descarga.download()
                base, ext = os.path.splitext(downloaded_file)
                mp3_file = base + ".mp3"
                video_clip = VideoFileClip(base + ".mp4")
                video_clip.audio.write_audiofile(mp3_file)
                video_clip.close()
                os.remove(base + ".mp4")
                st.write("Descarga completa")
                CancionActual = i
            except Exception as e:
                st.write(f"Error al descargar la canción No. : {e}")
                ListaDeReproduccion(link, CancionActual)

def DescargarVideo(link):
    yt = YouTube(link)
    st.write(f"Downloading: {yt.title}")
    try:
        yt.streams.filter(progressive=True, file_extension="mp4").first().download()
        st.write("Descarga completa")
    except Exception as e:
        st.write(f"Ocurrió un error: {e}")

def DescargarMusica(link):
    yt = YouTube(link)
    try:
        st.write("Comenzando Descarga")
        video = yt.streams.filter(progressive=True, file_extension="mp4").first()
        downloaded_file = video.download()
        base, ext = os.path.splitext(downloaded_file)
        mp3_file = base + ".mp3"
        video_clip = VideoFileClip(base + ".mp4")
        video_clip.audio.write_audiofile(mp3_file)
        video_clip.close()
        os.remove(base + ".mp4")
        st.write("Descarga completa")
    except Exception as e:
        st.write(f"Error al descargar la canción No. : {e}")

# Interfaz de usuario con Streamlit
st.title("Descargador de YouTube")
st.write("Ingrese la URL del video o playlist de YouTube:")

link = st.text_input("URL de YouTube")
opcion = st.radio("¿Qué desea descargar?", ("Video", "Audio", "Playlist"))

if st.button("Iniciar descarga"):
    if link:
        if opcion == "Video":
            DescargarVideo(link)
        elif opcion == "Audio":
            DescargarMusica(link)
        elif opcion == "Playlist":
            R2 = st.number_input("Desde qué canción comenzar (0 para comenzar desde el principio):", min_value=0, value=0)
            ListaDeReproduccion(link, R2)
    else:
        st.write("Por favor, ingrese una URL válida.")
