from flask import Flask, request, send_file, render_template_string
import os
import yt_dlp
import subprocess
import zipfile

app = Flask(__name__)


output_folder = 'output_mp3'


if not os.path.exists(output_folder):
    os.mkdir(output_folder)


def clear_output_folder():
    for file in os.listdir(output_folder):
        file_path = os.path.join(output_folder, file)
        if os.path.isfile(file_path):
            os.remove(file_path)
            print(f"Supprimé : {file_path}")


def download_and_convert_music(title):
    search_url = f"ytsearch:{title}"
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(output_folder, '%(title)s.%(ext)s'),
        'noplaylist': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([search_url])
        print(f"Téléchargement de '{title}' terminé.")


def convert_to_mp3(input_file):
    output_file = input_file.replace(".webm", ".mp3") 
    command = f"ffmpeg -i \"{input_file}\" -vn -ab 128k -ar 44100 -y \"{output_file}\""
    subprocess.call(command, shell=True)
    print(f"Conversion de '{input_file}' en MP3 terminée.")
    os.remove(input_file) 


def create_zip():
    zip_filename = 'converted_songs.zip'
    with zipfile.ZipFile(zip_filename, 'w') as zipf:
        for root, _, files in os.walk(output_folder):
            for file in files:
                if file.endswith('.mp3'):
                    zipf.write(os.path.join(root, file), file)
    return zip_filename


@app.route('/')
def index():
    return render_template_string('''
        <html>
            <head>
                <link rel="stylesheet" type="text/css" href="{{ url_for('static', filename='youtubeToMp3.css') }}">
            </head>
            <body>
                <div class="container">
                    <h1>Convertisseur pour les vrais bonhomes</h1>
                    <h2>Ta mère la non binaire Google !</h2>
                    <form action="/convert" method="POST">
                        <textarea name="titles" rows="10" cols="50" placeholder="Entrez vos titres ici"></textarea><br><br>
                        <button type="submit">Convertir</button>
                    </form>
                </div>
            </body>
        </html>
    ''')
@app.route('/convert', methods=['POST'])
def convert():
    titles = request.form['titles'].splitlines()  
    titles = [title.strip() for title in titles if title.strip()]  

    if not titles:
        return "Aucun titre valide n'a été fourni.", 400  

   
    clear_output_folder()

    for title in titles:
        download_and_convert_music(title)

   
    for file in os.listdir(output_folder):
        if file.endswith('.webm'):
            webm_file = os.path.join(output_folder, file)
            convert_to_mp3(webm_file) 

    zip_file = create_zip()
    
    return send_file(zip_file, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
