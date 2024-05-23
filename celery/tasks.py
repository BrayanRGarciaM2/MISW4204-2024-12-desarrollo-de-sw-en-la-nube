import os
import subprocess
import time
import uuid
import json
import pytube

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker
from google.cloud import storage
#from celery import Celery
from google.auth.exceptions import DefaultCredentialsError
from google.cloud import pubsub_v1
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, update

#celery = Celery('tasks', backend='redis://redis:6379/0', broker='redis://redis:6379/0')
db_url = "postgresql://postgres:123456@10.49.112.3:5432/videos"
engine = create_engine(db_url)

metadata = MetaData()
metadata.reflect(bind=engine)

Tareas = metadata.tables["tareas"]

Session = sessionmaker(bind=engine)
session = Session()

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
    os.chmod("/usr/src/celery/adjust_video.sh", 0o777)
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

def add_logo(video_path, id):
    # Definir los parámetros
    os.chmod("/usr/src/celery/add_image.sh", 0o777)
    input_path = video_path
    output_path = f"/usr/src/app/videos/{id}-temporal-add.mp4"
    # Llamar al script de shell desde Python
    try:
        subprocess.run(['./add_image.sh', input_path, output_path])
        os.replace(output_path, input_path)

    except subprocess.CalledProcessError as e:
        if os.path.exists(output_path):
            os.remove(output_path)
        print("Error al recortar el video. No se han realizado cambios en el archivo original.")

def trim_video(video, id):
    # Definir los parámetros
    os.chmod("/usr/src/celery/trim_video.sh", 0o777)
    input_path = video
    output_path = f"/usr/src/app/videos/{id}_temporal.mp4"
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


def editVideo(message):
    data = json.loads(message.data.decode('utf-8'))
    id_unico = data["id"]
    url = data["url"]
    message.ack()
    yt = pytube.YouTube(url)

    video = yt.streams.get_lowest_resolution()

    ruta_completa = '/usr/src/app/videos'
    video_src = ruta_completa + '/' + id_unico + '.mp4'
    video.download(output_path=ruta_completa, filename=id_unico + '.mp4')

    original_file_name = id_unico + '.mp4'

    try:
        client = storage.Client.from_service_account_json('/usr/src/celery/assets/idrl-videos-202410-88905e13ff46.json')
        bucket_name = 'videos-bucket-idrl'

        bucket = client.bucket(bucket_name)

        blob = bucket.blob(original_file_name)
        blob.upload_from_filename(video_src)

        trim_video(video_src, id_unico)
        #edit_ratio(video_src)
        add_logo(video_src, id_unico)

        edit_file_name = id_unico + '_Edited.mp4'

        blob = bucket.blob(edit_file_name)
        blob.upload_from_filename(video_src)
        print("id:", id_unico)
        new_result = "https://storage.cloud.google.com/videos-bucket-idrl/" + edit_file_name
        session.query(Tareas).filter(Tareas.c.id_task == id_unico).update({"status": "PROCESSED", "result": new_result})
        session.commit()
        session.close()
    except DefaultCredentialsError as e:
        print("Error de autenticación: las credenciales predeterminadas son inválidas o no están configuradas correctamente.", e)
        # Realizar acciones para solucionar el problema, como proporcionar nuevas credenciales
    except SQLAlchemyError as e:
        print("Ocurrió un error de SQLAlchemy:", e)
    except Exception as e:
        print("Se produjo un error durante la autenticación:", e)

topic_name = 'projects/{project_id}/topics/{topic}'.format(
    project_id="idrl-videos-202410",
    topic='MyTopic',  # Set this to something appropriate.
)

subscription_name = 'projects/{project_id}/subscriptions/{sub}'.format(
    project_id="idrl-videos-202410",
    sub='MyNew-sub',  # Set this to something appropriate.
)

def callback(message):
    data = json.loads(message.data.decode('utf-8'))
    id_unico = data["id"]
    url = data["url"]
    print("Prueba del mensaje: ", id_unico)
    message.ack()

with pubsub_v1.SubscriberClient() as subscriber:
    future = subscriber.subscribe(subscription_name, editVideo)
    try:
        future.result()
    except KeyboardInterrupt:
        future.cancel()
