import os
import requests

# URL ของไฟล์ JSON และ Discord Webhook
JSON_URL = "http://storage.googleapis.com/ro-sea-notice/90-1.json"
WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")
STATE_FILE = "last_content.txt"


def main():
  # ดึงข้อมูล JSON ปัจจุบัน
  response = requests.get(JSON_URL)
  if response.status_code != 200:
    return
  current_content = response.text

  # อ่านค่าเก่าที่เคยบันทึกไว้
  last_content = ""
  if os.path.exists(STATE_FILE):
    with open(STATE_FILE, "r", encoding="utf-8") as f:
      last_content = f.read()

  # ถ้าเนื้อหาไม่เหมือนเดิม ให้แจ้งเตือนและบันทึกค่าใหม่
  if current_content != last_content:
    message = {
        "content": (
            "🚨 **แจ้งเตือน!** พบการอัพเดทข้อมูลใหม่ในไฟล์ JSON:\n"
            f"🔗 {JSON_URL}"
        )
    }
    requests.post(WEBHOOK_URL, json=message)

    with open(STATE_FILE, "w", encoding="utf-8") as f:
      f.write(current_content)


if __name__ == "__main__":
  main()
