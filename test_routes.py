# test_routes.py
import unittest
from app import app  # アプリのインスタンスを作成するファクトリ関数

class TestRedisRoutes(unittest.TestCase):
    def setUp(self):
        self.app = app  # Flaskアプリを作成
        self.client = self.app.test_client()  # テストクライアントを作成

    def test_set_and_get(self):
        # POSTリクエストでデータを設定
        response = self.client.post('/set_example')
        self.assertEqual(response.status_code, 200)

        # GETリクエストでデータを取得
        response = self.client.get('/get_example')
        data = response.get_json()
        self.assertEqual(data['example_key'], 'Hello from Redis!')

if __name__ == '__main__':
    unittest.main()
