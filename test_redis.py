# test_redis.py
from models.redis_client import get_redis_client

def test_redis():
    client = get_redis_client()

    # テストデータの設定
    client.set('test_key', 'Hello, Redis!')

    # データの取得
    value = client.get('test_key')
    print(f"Value from Redis: {value}")

if __name__ == '__main__':
    test_redis()
