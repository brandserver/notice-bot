import datetime
import json
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
    try:
      data = response.json()

      # ดึงค่า Timestamp (start และ end) จาก JSON
      start_ts = data.get("start")
      end_ts = data.get("end")

      # แปลง Timestamp เป็นวันที่และเวลาแบบสากล (UTC / อ่านง่าย)
      start_str = (
          datetime.datetime.fromtimestamp(
              start_ts, datetime.timezone.utc
          ).strftime("%Y-%m-%d %H:%M:%S UTC")
          if start_ts
          else "N/A"
      )
      end_str = (
          datetime.datetime.fromtimestamp(
              end_ts, datetime.timezone.utc
          ).strftime("%Y-%m-%d %H:%M:%S UTC")
          if end_ts
          else "N/A"
      )

      # จัดรูปแบบข้อความให้แสดงแค่วันที่และเวลา
      notification_text = (
          f"@everyone 🚨 **New Notice Update**\n\n"
          f"📅 **Start:** {start_str}\n"
          f"📅 **End:** {end_str}"
      )

      message = {"content": notification_text}
      requests.post(WEBHOOK_URL, json=message)

    except Exception as e:
      # กรณีเกิดข้อผิดพลาด ให้แจ้งเตือนแบบสำรอง
      fallback_message = {
          "content": (
              f"@everyone 🚨 **New Notice Update detected (Timestamp parse"
              f" error)**\n🔗 {JSON_URL}"
          )
      }
      requests.post(WEBHOOK_URL, json=fallback_message)

    # บันทึกสถานะปัจจุบันลงไฟล์
    with open(STATE_FILE, "w", encoding="utf-8") as f:
      f.write(current_content)


if __name__ == "__main__":
  main()
