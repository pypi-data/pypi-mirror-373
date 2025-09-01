from flask import Flask, send_from_directory, request, make_response, jsonify

app = Flask(__name__)
app.config.update(dict(UPLOAD_FOLDER=r'D:\xmov\projects\git.xmov\ttsa_backend\ttsa_backend'))


@app.route('/ttsa/offline')
def hello():
    text = request.json.get('text', '')
    if text is '':
        data = dict(error=-1, msg='invalid text', data=dict())
    else:
        data = dict(error=0, msg='success', data=dict(h264='', pcm=''))
    return make_response(jsonify(data), 200)


@app.route('/ttsa/download/<path:filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename, as_attachment=True)


if __name__ == "__main__":
    app.run(port=5000, debug=True)
