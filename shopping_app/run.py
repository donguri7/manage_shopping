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
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
