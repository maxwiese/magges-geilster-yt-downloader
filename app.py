from __future__ import unicode_literals
from flask import Flask, render_template, request, send_from_directory, current_app
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests
import youtube_dl
import os


class SearchBarForm(FlaskForm):
    search_term = StringField('SearchTerm', validators=[DataRequired()])
    submit = SubmitField('Search')


app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("secret_key")
api_key = os.getenv("api_key")


@app.route('/', methods=['GET', 'POST'])
def index():
    form = SearchBarForm()

    if form.is_submitted():
        search_term = form.search_term.data
        search_result = requests.get(
            f'https://www.googleapis.com/youtube/v3/search?part=snippet&maxResults=42&q={search_term}&key={api_key}')
        items = search_result.json()['items']

        return render_template('results.html', result=items)

    return render_template('index.html', form=form)


@app.route('/result', methods=['GET', 'POST'])
def result():
    return render_template('results.html')


@app.route('/download', methods=['GET', 'POST'])
def download():
    url = request.form['url']

    ydl_opts = {
        'writethumbnail': True,
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192'},
            {'key': 'EmbedThumbnail'}],
        'call_home': False,
        'progress_hooks': [pg_hook],
        'outtmpl': '%(title)s.%(ext)s'
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        file = filename[:-4] + "mp3"

    return send_from_directory(directory=current_app.root_path, filename=file, as_attachment=True)


def pg_hook(d):
    if d['status'] == 'finished':
        print('Done downloading, now converting ...')


if __name__ == '__main__':
    app.run(host='0.0.0.0')
