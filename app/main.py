from flask import send_from_directory
from flask import Flask, flash, request, redirect, url_for
from werkzeug.utils import secure_filename
from flask import render_template
from url_utils import get_base_url
import os
import model

# setup the webserver
# port may need to be changed if there are multiple flask servers running on same server
port = 12345
base_url = get_base_url(port)

# if the base url is not empty, then the server is running in development, and we need to specify the static folder so that the static files are served
if base_url == '/':
  app = Flask(__name__)
else:
  app = Flask(__name__, static_url_path=base_url + 'static')

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024


def allowed_file(filename):
  return '.' in filename and \
         filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route(f'{base_url}', methods=['GET', 'POST'])
def home():
  if request.method == 'POST':
    # check if the post request has the file part
    if 'file' not in request.files:
      flash('No file part')
      return redirect(request.url)

    file = request.files['file']
    # if user does not select file, browser also
    # submit an empty part without filename
    if file.filename == '':
      flash('No selected file')
      return redirect(request.url)

    if file and allowed_file(file.filename):
      filename = secure_filename(file.filename)
      file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
      return redirect(url_for('uploaded_file', filename=filename))

  return render_template('home.html')


@app.route(f'{base_url}/uploads/<filename>')
def uploaded_file(filename):
  here = os.getcwd()
  image_path = os.path.join(here, app.config['UPLOAD_FOLDER'], filename)
  results = model.query(image_path)
  if len(results) > 0:
    confidences = results['score']
    
    # confidences: rounding and changing to percent, putting in function
    format_confidences = str(round(confidences * 100)) + '%'
    
    labels = results['label'].capitalize()
    # labels: sorting and capitalizing, putting into function
    return render_template('results.html',
                        confidences=format_confidences,
                           labels=labels,
                           old_filename=filename,
                           filename=filename)
  elif "error" in res:
    return render_template('results.html',
                           labels='no pet',
                           old_filename=filename,
                           filename=filename)
  else:
    return render_template('results.html',
                           labels='no pet',
                           old_filename=filename,
                           filename=filename)


@app.route(f'{base_url}/uploads/<path:filename>')
def files(filename):
  return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)


# define additional routes here
# for example:
# @app.route(f'{base_url}/team_members')
# def team_members():
#     return render_template('team_members.html') # would need to actually make this page

if __name__ == '__main__':
  # IMPORTANT: change url to the site where you are editing this file.
  website_url = 'localhost'

  print(f'Try to open\n\n    https://{website_url}' + base_url + '\n\n')
  app.run(host='0.0.0.0', port=port, debug=True)
