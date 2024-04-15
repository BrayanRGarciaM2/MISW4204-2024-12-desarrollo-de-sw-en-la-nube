#!/bin/bash

# Comprueba que se hayan proporcionado todos los argumentos necesarios.
if [ "$#" -ne 4 ]; then
    echo "Uso: $0 <archivo_entrada> <tiempo_inicio> <duración> <archivo_salida>"
    exit 1
fi

# Asigna cada parámetro a una variable para mejorar la legibilidad.
input_file="$1"
start_time="$2"
duration="$3"
output_file="$4"

# Ejecuta ffmpeg para recortar el video.
ffmpeg -i "$input_file" -ss "$start_time" -t "$duration" -c copy "$output_file"

echo "Video recortado guardado como $output_file"