import os
from datetime import datetime
from flask import flash, request, url_for, make_response, send_file
from flask_restful import Resource
from werkzeug.utils import secure_filename
from speedangle_2_racechrono import (
    read_speedangle_file,
    speedangle_to_racechrono_vbo,
    write_racechrono_file,
)

ALLOWED_EXTENSIONS = {"txt", "log", "sa"}
UPLOAD_FOLDER = "/tmp/"


class SourceFile(Resource):
    def post(self):

        if "file" not in request.files:
            return {"message": "No file provided"}, 400
        file = request.files["file"]

        if file.filename == "":
            return {"message": "Blank filename received"}, 400

        if file and not self.allowed_file(file.filename):
            return {"message": "Unrecognized file type"}, 400

        filename = secure_filename(file.filename)
        file.save(UPLOAD_FOLDER + filename)

        converted_file = self.convert_filetypes(filename)

        try:
            return send_file(UPLOAD_FOLDER + converted_file, as_attachment=True)
        finally:
            os.remove(UPLOAD_FOLDER + filename)
            os.remove(UPLOAD_FOLDER + converted_file)

    def get(self):
        headers = {"Content-Type": "text/html"}
        html = """
        <!doctype html>
        <title>Upload new File</title>
        <h1>Upload new File</h1>
        <form method=post enctype=multipart/form-data>
            <input type=file name=file>
            <input type=submit value=Upload>
        </form>
        """
        return make_response(html, 200, headers)

    def allowed_file(self, filename):
        return (
            "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
        )

    def convert_filetypes(self, filename):

        output_filename = (
            filename.rsplit(".", 1)[0] + "_" + datetime.now().strftime("%s") + ".vbo"
        )

        timestamp, line_data = read_speedangle_file(UPLOAD_FOLDER + filename)
        rc_lines = speedangle_to_racechrono_vbo(timestamp, line_data)
        write_racechrono_file(rc_lines, UPLOAD_FOLDER + output_filename)

        return output_filename
