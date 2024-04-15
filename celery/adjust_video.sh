#!/bin/bash

# Este script requiere dos parámetros: el archivo de entrada y el archivo de salida.
input_file="$1"
output_file="$2"
width="$3"
height="$4"

# Comando ffmpeg para cambiar el tamaño y ajustar el video.
ffmpeg -i "$input_file" -vf "scale=$width:$height:force_original_aspect_ratio=decrease,pad=$width:$height:(ow-iw)/2:(oh-ih)/2" "$output_file"
