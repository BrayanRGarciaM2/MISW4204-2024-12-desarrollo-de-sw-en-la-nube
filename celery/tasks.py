
import os
import subprocess
import time
import uuid

import pytube

from google.cloud import storage
from celery import Celery
from google.auth.exceptions import DefaultCredentialsError


celery = Celery('tasks', backend='redis://redis:6379/0', broker='redis://redis:6379/0')

def generar_id_unico():
    """
    Genera un ID único utilizando uuid4.

    Returns:
        str: ID único en formato hexadecimal.
    """
    return str(uuid.uuid4())

def obtener_nombre_archivo(ruta):
    # Dividir la ruta en el directorio y el nombre del archivo
    directorio, nombre_archivo = os.path.split(ruta)
    # Obtener solo el nombre del archivo con la extensión
    nombre_archivo_con_extension = nombre_archivo.split("/")[-1]
    return nombre_archivo_con_extension

def edit_ratio(video):
    # Definir los parámetros
    input_path = video
    output_path = f"/usr/src/app/videos/temporal.mp4"
    width = '640'
    height = '360'

    # Llamar al script de shell desde Python
    try:
        subprocess.run(['./adjust_video.sh', input_path, output_path, width, height])        
        os.replace(output_path, input_path)
        fileName = obtener_nombre_archivo(input_path)
        blob = bucket.blob(fileName)
        blob.upload_from_filename(fileName)
    except subprocess.CalledProcessError as e:
        # Si hay un error, asegúrate de eliminar el archivo temporal
        if os.path.exists(output_path):
            os.remove(output_path)
        print("Error al recortar el video. No se han realizado cambios en el archivo original.")

def add_logo(video_path):
    # Definir los parámetros
    input_path = video_path
    output_path = f"/usr/src/app/videos/temporal.mp4"
    output_path = "temporal.mp4"
    # Llamar al script de shell desde Python
    try:
        subprocess.run(['./add_image.sh', input_path, output_path])
        os.replace(output_path, input_path)

    except subprocess.CalledProcessError as e:
        if os.path.exists(output_path):
            os.remove(output_path)
        print("Error al recortar el video. No se han realizado cambios en el archivo original.")

def trim_video(video):
    # Definir los parámetros
    input_path = video
    output_path = f"/usr/src/app/videos/temporal.mp4"
    output_path = "temporal.mp4"
    start_time = '00:00:00'
    duration = '20'

    # Llamar al script de shell desde Python
    try:
        subprocess.run(['./trim_video.sh', input_path, start_time, duration, output_path])
        os.replace(output_path, input_path)
    except subprocess.CalledProcessError as e:
        # Si hay un error, asegúrate de eliminar el archivo temporal
        if os.path.exists(output_path):
            os.remove(output_path)
        print("Error al recortar el video. No se han realizado cambios en el archivo original.")


@celery.task(name='tasks.edit')
def editVideo(url):


    yt = pytube.YouTube(url)

    id_unico = generar_id_unico()
    video = yt.streams.get_lowest_resolution()

    ruta_completa = '/usr/src/app/videos'
    video_src = ruta_completa + '/' + id_unico + '.mp4'
    video.download(output_path=ruta_completa, filename=id_unico + '.mp4')

    original_file_name = id_unico + '.mp4'

    try:
        client = storage.Client()
        bucket_name = 'videos-bucket-idrl'

        bucket = client.bucket(bucket_name)

        blob = bucket.blob(original_file_name)
        blob.upload_from_filename(video)

        trim_video(video_src)
        edit_ratio(video_src)   

        edit_file_name = id_unico + '_Edited.mp4'

        blob = bucket.blob(edit_file_name)
        blob.upload_from_filename(edit_file_name)

    except DefaultCredentialsError as e:
        print("Error de autenticación: las credenciales predeterminadas son inválidas o no están configuradas correctamente.")
    # Realizar acciones para solucionar el problema, como proporcionar nuevas credenciales
    except Exception as e:
        print("Se produjo un error durante la autenticación:", e)
    

  

    
