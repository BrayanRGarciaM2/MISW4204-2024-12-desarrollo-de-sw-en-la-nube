import time
import uuid

import pytube
from moviepy.video.io.VideoFileClip import VideoFileClip
import moviepy.editor as mp

from celery import Celery

celery = Celery('tasks', backend='redis://redis:6379/0', broker='redis://redis:6379/0')

def generar_id_unico():
    """
    Genera un ID único utilizando uuid4.

    Returns:
        str: ID único en formato hexadecimal.
    """
    return str(uuid.uuid4())

def edit_logo(video):
    aspect_ratio = (16, 9)

    original_width, original_height = video.size
    new_width = int(original_height * aspect_ratio[1] / aspect_ratio[0])
    new_height = int(new_width * aspect_ratio[0] / aspect_ratio[1])

    # Carga el logo y lo escala.
    logo = mp.ImageClip(logo_path)
    logo_scale = min(new_width / logo.width, new_height / logo.height)
    scaled_logo = logo.resize((int(logo.width * logo_scale), int(logo.height * logo_scale)))
    # Crea overlays para el logo en el inicio y final.
    initial_overlay = mp.CompositeVideoClip([video_recortado, scaled_logo.set_pos('center')], size=video_recortado.size)
    initial_overlay = initial_overlay.set_duration(1)

@celery.task(name='tasks.edit')
def editVideo(url):
    # os.system('youtube-dl '+url)
    duracion_segundos = 20


    yt = pytube.YouTube(url)

    id_unico = generar_id_unico()

    video = yt.streams.get_lowest_resolution()

    ruta_completa = '/usr/src/app/videos'
    video.download(output_path=ruta_completa, filename=id_unico + '.mp4')

    video_clip = VideoFileClip(filename=ruta_completa + '/' + id_unico + '.mp4')
    audio_clip = video_clip.audio

    audio_recortado = audio_clip.subclip(0, duracion_segundos)
    video_recortado = video_clip.subclip(0, duracion_segundos)

    # Combina el audio y el video recortados y guarda el archivo final.
    video_final = video_recortado.set_audio(audio_recortado)
    video_final.write_videofile(id_unico + '.mp4')