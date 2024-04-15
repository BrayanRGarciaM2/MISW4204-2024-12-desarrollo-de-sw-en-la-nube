#!/bin/bash
# Variables
input_file="$1"
final_video_path="$2"
image_file="./assets/drl-logo.png"  # Asegúrate de cambiar 'tu_imagen.png' por el nombre de tu imagen
intro_clip="intro.mp4"
outro_clip="outro.mp4"
temp_list="file_list.txt"

# Crear clips de video desde la imagen con escala específica
ffmpeg -loop 1 -framerate 25 -i "$image_file" -c:v libx264 -t 0.4 -pix_fmt yuv420p -vf "scale=480:360" -r 25 "$intro_clip"
ffmpeg -loop 1 -framerate 25 -i "$image_file" -c:v libx264 -t 0.4 -pix_fmt yuv420p -vf "scale=480:360" -r 25 "$outro_clip"

# Crear un archivo de lista para la concatenación
echo "file '$intro_clip'" > "$temp_list"
echo "file '$input_file'" >> "$temp_list"
echo "file '$outro_clip'" >> "$temp_list"

# Concatenar los clips, re-codificando para asegurar compatibilidad
ffmpeg -f concat -safe 0 -i "$temp_list" -c:v libx264 -c:a aac -pix_fmt yuv420p -r 2 "$final_video_path"

# Limpiar archivos temporales
rm "$intro_clip" "$outro_clip" "$temp_list"

echo "El video final está listo: $final_video_path"
