# main.py (FastAPI)
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse
import boto3
from botocore.exceptions import NoCredentialsError

app = FastAPI()

# Configura las credenciales de AWS S3
AWS_ACCESS_KEY = 'AKIA3WOWM4NIBFGEBVGR'
AWS_SECRET_KEY = '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'
AWS_BUCKET_NAME = 'conconcrefotos'
AWS_REGION = 'us-east-2'

s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY, region_name=AWS_REGION)

html_content = """
<html>
    <head>
        <script>
            function handleDrop(event) {
                event.preventDefault();
                const fileInput = document.getElementById('fileInput');
                fileInput.files = event.dataTransfer.files;
                displayFileName(fileInput);
            }

            function displayFileName(input) {
                const fileNameDisplay = document.getElementById('fileName');
                fileNameDisplay.innerText = input.files.length > 0 ? "Archivos seleccionados: " + input.files[0].name : "";
            }
        </script>
    </head>
    <body>
        <div id="dropArea" ondrop="handleDrop(event)" ondragover="event.preventDefault()">
            <form action="/uploadfile/" enctype="multipart/form-data" method="post">
                <input type="file" id="fileInput" name="file" multiple style="display: none;" onchange="displayFileName(this)">
                <label for="fileInput" style="cursor: pointer;">Arrastra y suelta archivos aquí o haz clic para seleccionar archivos.</label>
                <p id="fileName"></p>
                <input type="submit">
            </form>
        </div>

        <hr>

        <h2>Documentos en el Bucket:</h2>
        <table border="1">
            <tr>
                <th>Nombre del Documento</th>
                <th>Enlace</th>
            </tr>
            {% for document in documents %}
                <tr>
                    <td>{{ document['Key'] }}</td>
                    <td><a href="{{ document['Link'] }}" target="_blank">Ver</a></td>
                </tr>
            {% endfor %}
        </table>
    </body>
</html>
"""

def get_s3_documents():
    try:
        # Obtiene la lista de objetos en el bucket S3
        response = s3.list_objects(Bucket=AWS_BUCKET_NAME)
        return response.get('Contents', [])
    except NoCredentialsError:
        return []

@app.get("/", response_class=HTMLResponse)
def home():
    documents = get_s3_documents()
    return HTMLResponse(content=html_content.replace("{% for document in documents %}", "{% for document in documents %}".replace("[]", str(documents))))

@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile = File(...)):
    try:
        # Sube el archivo al bucket S3
        s3.upload_fileobj(file.file, AWS_BUCKET_NAME, file.filename)
        return {"filename": file.filename, "message": "Archivo subido correctamente"}
    except NoCredentialsError:
        return {"error": "Credenciales de AWS no configuradas"}
