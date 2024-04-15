import os
import time
import uuid

import cv2
import pytube
import subprocess

from moviepy.video.compositing.concatenate import concatenate
from moviepy.video.io.ImageSequenceClip import ImageSequenceClip
from moviepy.video.io.VideoFileClip import VideoFileClip

from celery import Celery

celery = Celery('tasks', backend='redis://redis:6379/0', broker='redis://redis:6379/0')

def generar_id_unico():
    """
    Genera un ID único utilizando uuid4.

    Returns:
        str: ID único en formato hexadecimal.
    """
    return str(uuid.uuid4())

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
    except subprocess.CalledProcessError as e:
        # Si hay un error, asegúrate de eliminar el archivo temporal
        if os.path.exists(output_path):
            os.remove(output_path)
        print("Error al recortar el video. No se han realizado cambios en el archivo original.")

def add_logo(video_path):
    # Definir los parámetros
    input_path = video_path
    output_path = f"/usr/src/app/videos/temporal.mp4"
    # Llamar al script de shell desde Python
    try:
        subprocess.run(['./add_image.sh', input_path, output_path])
        os.replace(output_path, input_path)

    except subprocess.CalledProcessError as e:
        if os.path.exists(output_path):
            os.remove(output_path)
        print("Error al recortar el video. No se han realizado cambios en el archivo original.")

    # Definir rutas de archivos
    # intro_image_path = "./assets/drl-logo.png"
    #
    # imagen = cv2.imread(intro_image_path)
    #
    # fps = 2
    # ancho, alto = imagen.shape[:2]
    #
    # # Crear el objeto VideoWriter
    # fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    # video = cv2.VideoWriter('video.mp4', fourcc, fps, (ancho, alto))
    #
    # # Generar el video
    # num_veces = 2
    #
    # for i in range(num_veces):
    #     video.write(imagen)
    #
    # # Liberar los recursos
    # video.release()


def trim_video(video):
    # Definir los parámetros
    input_path = video
    output_path = f"/usr/src/app/videos/temporal.mp4"
    start_time = '00:00:00'
    duration = '18'

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
    # os.system('youtube-dl '+url)
    duracion_segundos = 20


    yt = pytube.YouTube(url)

    id_unico = generar_id_unico()

    video = yt.streams.get_lowest_resolution()

    ruta_completa = '/usr/src/app/videos'
    video_src = ruta_completa + '/' + id_unico + '.mp4'
    video.download(output_path=ruta_completa, filename=id_unico + '.mp4')

    trim_video(video_src)
    edit_ratio(video_src)


    # if video_clip.duration > duracion_segundos:
    #     video_recortado = video_clip.subclip(0, duracion_segundos)
    #     video_recortado.write_videofile(ruta_completa + '/' + id_unico + '.mp4')
    # else:
    # video_clip.write_videofile(ruta_completa + '/' + id_unico + '.mp4')
