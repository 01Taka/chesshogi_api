# redis_client.py
import redis
import os
from dotenv import load_dotenv

# .envファイルをロード（ローカル環境用）
load_dotenv()

def get_redis_client():
    # 環境変数から接続情報を取得
    redis_host = os.getenv('REDIS_HOST', 'localhost')
    redis_port = int(os.getenv('REDIS_PORT', 6379))
    redis_password = os.getenv('REDIS_PASSWORD', None)
    
    # "true" / "false" を Python の bool に変換
    redis_ssl = os.getenv('REDIS_SSL', 'true').lower() == 'true'

    # Redisクライアントを作成
    return redis.StrictRedis(
        host=redis_host,
        port=redis_port,
        password=redis_password,
        ssl=redis_ssl,
        decode_responses=True
    )
