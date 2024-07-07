import json
import re
from flask import current_app
import os

def clean_item_name(item):
    # 一般的なクリーニングルール
    item = re.sub(r'[#♯]\d+', '', item)
    item = re.sub(r'¥\d+(\s*x\s*\d+)?', '', item)
    item = re.sub(r'@\d+(\s*x\s*\d+)?', '', item)
    item = re.sub(r'\d+個', '', item)
    item = re.sub(r'^[リF♯]:?\s*', '', item)
    item = re.sub(r'\s*#\d+$', '', item)
    item = re.sub(r'\s+', ' ', item)
    return item.strip()

def is_valid_item(item):
    invalid_patterns = [
        '#」', '-', 'リ#', 'R0035', '軽減税率', 'バイオマスレジ袋', '値引', '商品代金',
        r'^\d{4}年\d{1,2}月\d{1,2}日',
        r'\d{1,2}:\d{2}',
        r'^[#♯]\d+$',
        r'^\*\d+$',
        r'^,\d+\)$',
    ]
    return (len(item) > 1 and 
            not any(re.search(pattern, item) for pattern in invalid_patterns) and
            not item.isdigit())

def normalize_item_name(item):
    item = re.sub(r'(\d+)ml', r'\1mL', item)
    item = re.sub(r'(\d+)L', r'\1L', item)
    item = re.sub(r'\s', '', item)
    return item

def extract_items(lines):
    items = []
    start_flag = False
    end_flag = False
    for line in lines:
        if re.search(r'領収書|明細|商品名', line):
            start_flag = True
            continue
        
        if re.search(r'小計|合計|税|お預り', line):
            end_flag = True
        
        if start_flag and not end_flag:
            item = clean_item_name(line)
            if is_valid_item(item):
                items.append(normalize_item_name(item))
    
    return items

def process_receipt(json_data):
    return extract_items(json_data['lines'])

def json_to_products(json_path):
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        items = process_receipt(data)
        
        # 結果をJSONファイルとして保存
        output_dir = current_app.config.get('PRODUCT_OUTPUT_FOLDER', 'product_outputs')
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        output_filename = os.path.basename(json_path).replace('.json', '_products.json')
        output_path = os.path.join(output_dir, output_filename)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump({"商品名": items}, f, ensure_ascii=False, indent=2)
        
        return output_path
    except Exception as e:
        print(f"Error processing JSON file: {e}")
        return None

# この部分は単体テスト用です。実際のアプリケーションでは削除または修正してください。
if __name__ == "__main__":
    from flask import Flask
    app = Flask(__name__)
    app.config['PRODUCT_OUTPUT_FOLDER'] = 'product_outputs'
    
    with app.app_context():
        # テスト用のJSONファイルパス
        test_json_path = 'path/to/your/test.json'
        result = json_to_products(test_json_path)
        if result:
            print(f"Products extracted and saved to: {result}")
        else:
            print("Failed to extract products")