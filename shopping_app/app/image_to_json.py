from google.cloud import vision
import os
import json
from flask import current_app
from werkzeug.utils import secure_filename
import logging
import base64

if "GOOGLE_CREDENTIALS" in os.environ:
    credentials_path = "/tmp/creds.json"
    with open(credentials_path, "wb") as f:
        f.write(base64.b64decode(os.environ["GOOGLE_CREDENTIALS"]))
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path

# Google Cloud vision client init
client = vision.ImageAnnotatorClient()

logger = logging.getLogger(__name__)

def detect_text(image_content):
    """画像コンテンツからテキストを検出する"""
    image = vision.Image(content=image_content)
    response = client.text_detection(image=image)
    
    if response.error.message:
        raise Exception(
            '{}\nFor more info on error messages, check: '
            'https://cloud.google.com/apis/design/errors'.format(
                response.error.message)
        )
    
    return response

def extract_lines(text):
    return [line.strip() for line in text.split('\n') if line.strip()]

def image_to_json(uploaded_file):
    """
    アップロードされたファイルを処理し、JSONを生成する
    
    :param uploaded_file: Flask's FileStorage object
    :return: 生成されたJSONファイルのパス、またはNone（失敗時）
    """
    try:
        if uploaded_file.filename == '':
            return None

        # セキュアなファイル名を生成
        filename = secure_filename(uploaded_file.filename)
        
        # 一時的にファイルを保存
        temp_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        uploaded_file.save(temp_path)

        try:
            # 画像ファイルを読み込む
            with open(temp_path, 'rb') as image_file:
                content = image_file.read()

            # テキスト検出
            response = detect_text(content)
            texts = response.text_annotations

            if texts:
                full_text = texts[0].description
                lines = extract_lines(full_text)
                
                # JSONデータを準備
                output_data = {
                    "lines": lines
                }
                
                # JSON出力用のディレクトリを準備
                output_dir = current_app.config.get('JSON_OUTPUT_FOLDER', 'json_outputs')
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir)
                
                # JSONファイルのパスを生成
                json_filename = os.path.splitext(filename)[0] + '.json'
                output_path = os.path.join(output_dir, json_filename)
                
                # JSONファイルに保存
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(output_data, f, ensure_ascii=False, indent=2)
                
                print(f"テキストの各行をJSONファイルに保存しました: {output_path}")
                return output_path
            else:
                print("テキストが検出されませんでした。")
                return None
        
        finally:
            # 一時ファイルを削除
            if os.path.exists(temp_path):
                os.remove(temp_path)
                
    except Exception as e:
        logger.error(f"Error in image_to_json: {str(e)}")
        raise

# 単体テスト用
if __name__ == "__main__":
    from flask import Flask
    app = Flask(__name__)
    app.config['UPLOAD_FOLDER'] = 'uploads'
    app.config['JSON_OUTPUT_FOLDER'] = 'json_outputs'
    
    with app.app_context():
        class MockFile:
            def __init__(self, filename):
                self.filename = filename
            
            def save(self, path):
                pass

        mock_file = MockFile('example.jpg')
        json_path = image_to_json(mock_file)
        if json_path:
            print(f"JSON file created at: {json_path}")
        else:
            print("Failed to create JSON file")