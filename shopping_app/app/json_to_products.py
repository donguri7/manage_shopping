import json
import re
from flask import current_app
import os
from datetime import datetime

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
        r'^\W+$',  # 記号のみ
        r'(営業時間|営業日|店舗|電話|TEL|FAX|住所|年中無休|開催|開店|会員|恒例)',  # 店舗情報に関する単語
        r'(領収書|レシート|控え|明細|合計|小計|税|お預り|おつり)',  # レシート関連の単語
        r'(セール|キャンペーン|特売|値引|割引|ポイント)',  # セール関連の単語
        r'(配送|宅配|送料|お届け)',  # 配送関連の単語
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
    items = extract_items(json_data['lines'])
    purchase_date = extract_purchase_date(json_data['lines'])
    return items, purchase_date

def extract_purchase_date(lines):
    date_pattern = r'\d{4}年\d{1,2}月\d{1,2}日'
    for line in lines:
        match = re.search(date_pattern, line)
        if match:
            date_str = match.group()
            try:
                return datetime.strptime(date_str, '%Y年%m月%d日').date()
            except ValueError:
                continue
    return datetime.now().date()  # デフォルトは現在の日付

def json_to_products(json_path):
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        items, purchase_date = process_receipt(data)
        
        # 結果をJSONファイルとして保存
        output_dir = current_app.config.get('PRODUCT_OUTPUT_FOLDER', 'product_outputs')
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        output_filename = os.path.basename(json_path).replace('.json', '_products.json')
        output_path = os.path.join(output_dir, output_filename)
        
        output_data = {
            "商品名": items,
            "購入日": purchase_date.isoformat()
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        
        return output_path
    except Exception as e:
        current_app.logger.error(f"Error processing JSON file: {e}")
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