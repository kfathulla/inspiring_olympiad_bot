from locust import HttpUser, task, between
import random

class BotUser(HttpUser):
    wait_time = between(0.1, 0.5)  # Simulate burst traffic
    host = "https://bot.metabio.uz"
    
    @task
    def submit_test(self):
        test_data = {
            "user_id": random.randint(1, 100000),
            "variant": f"TEST_{random.randint(1, 100)}"
        }
        self.client.post(
            "/webhook",
            json={
                "update_id": random.randint(1, 1000000),
                "message": {
                    "message_id": random.randint(1, 1000),
                    "from": {"id": test_data["user_id"], "is_bot": False},
                    "text": "/start"
                }
            },
            headers={"X-Telegram-Bot-Api-Secret-Token": "7718513238:AAGngpKcyBvSmJ-TX_lz9gFQYweG42Xcjro"}
        )