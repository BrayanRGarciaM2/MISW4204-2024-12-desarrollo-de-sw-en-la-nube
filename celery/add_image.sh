#!/bin/bash

# Variables
input_file="$1"
final_video_path="$2"
image_file="./assets/drl-logo.png"  # Replace with your image path
intro_clip_duration=1  # Duration of intro and outro clips (in seconds)
intro_clip_name="intro.mp4"
intro_clip_name_ts="intro2.ts"
outro_clip_name="outro.mp4"
outro_clip_name_ts="outro2.ts"
main_clip_name_ts="main.ts"
temp_list_file="file_list.txt"

#ffmpeg -i "$input_file" -i "$image_file" -filter_complex "
#    color=c=black:size=640x360 [temp]; \
#    [temp][1:v] overlay=x=0:y=0:enable='between(t,0,5)' [temp]; \
#    [0:v] setpts=PTS+5/TB, scale=640x360:force_original_aspect_ratio=decrease, pad=640:360:-1:-1:color=black [v:0]; \
#    [temp][v:0] overlay=x=0:y=0:shortest=1:enable='gt(t,5)' [v]; \
#    [0:a] asetpts=PTS+5/TB [a]" -map [v] -map [a] -preset veryfast "$final_video_path"

ffmpeg -i "$image_file" -vf "scale=1280:720" logo_scaled.png

ffmpeg -i "$input_file" -i logo_scaled.png -filter_complex \
"[0:v]scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2[v0]; \
 [v0][1:v]overlay=W-w-10:H-h-10:enable='between(t,0,1)+between(t,19,20)'[out]" \
-map "[out]" -c:v libx264 -c:a copy -aspect 16:9 "$final_video_path"

echo "Video editado con intro y outro: $final_video_path"
