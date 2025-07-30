from flask import Flask, request, jsonify
import subprocess
import os
import uuid

app = Flask(__name__)
UPLOAD_FOLDER = "./tmp"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/run-python', methods=['POST'])
def run_python():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    uploaded_file = request.files['file']
    if not uploaded_file.filename.endswith('.py'):
        return jsonify({"error": "Only .py files allowed"}), 400

    file_id = uuid.uuid4().hex
    file_path = os.path.join(UPLOAD_FOLDER, f"{file_id}.py")
    uploaded_file.save(file_path)

    try:
        result = subprocess.run(
            ["python3", file_path],
            capture_output=True,
            text=True,
            timeout=10
        )
        output = result.stdout
        error = result.stderr
        return jsonify({
            "stdout": output,
            "stderr": error,
            "returncode": result.returncode
        })

    except subprocess.TimeoutExpired:
        return jsonify({"error": "Execution timed out"}), 500

    finally:
        os.remove(file_path)

if __name__ == '__main__':
    app.run(debug=True)
