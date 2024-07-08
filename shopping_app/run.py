import cProfile
import logging
import resource
from app import create_app

# ログの設定
logging.basicConfig(level=logging.DEBUG)

app = create_app()

def profile_app(port=5001):
    # メモリ使用量を表示
    print(f"Initial Memory usage: {resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}")

    # アプリケーションの実行をプロファイリング
    cProfile.run(f'app.run(debug=True, port={port})', 'profiling_stats')

    # プロファイリング後のメモリ使用量を表示
    print(f"Final Memory usage: {resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}")

if __name__ == '__main__':
    # ポート番号を指定（デフォルトは5001）
    port = 5001

    # プロファイリングを行う場合
    # profile_app(port)

    # 通常の実行の場合（必要に応じてコメントアウトを解除）
    app.run(debug=True, port=port)
