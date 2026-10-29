import json
import os
import re
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

      # ดึงข้อมูลจากภาษาอังกฤษ (คีย์ "10")
      notice_data = data.get("10", {})
      msg_text = notice_data.get("msg", "")

      # แยกส่วน Title และ Content ออกจากกัน
      parts = msg_text.split("####content///")
      title = (
          parts[0].replace("####mainTitle///", "").replace("\n", " ").strip()
      )
      body = parts[1].replace("\\n", "\n").strip() if len(parts) > 1 else ""

      # ค้นหาเฉพาะประโยคที่มีคำว่า maintenance หรือเวลา เพื่อเอามาสรุปสั้นๆ (ถ้ามี)
      # หรือจะดึงบรรทัดแรกๆ ของเนื้อหามาแสดงก็ได้
      maintenance_info = "New maintenance schedule updated."
      for line in body.split("\n"):
        if "maintenance" in line.lower() or "gm" in line.lower():
          maintenance_info = line.strip()
          break

      # จัดรูปแบบข้อความที่จะส่งเข้า Discord
      notification_text = (
          f"@everyone 🚨 **Ragnarok M Notice Update**\n\n"
          f"📌 **Title:** {title}\n"
          f"⏰ **Details:** {maintenance_info}\n\n"
          f"🔗 {JSON_URL}"
      )

      message = {"content": notification_text}
      requests.post(WEBHOOK_URL, json=message)

    except Exception as e:
      # กรณีเกิดข้อผิดพลาด ให้ส่งลิงก์แจ้งเตือนทั่วไป
      fallback_message = {
          "content": (
              f"@everyone 🚨 **New Notice Update detected**\n🔗 {JSON_URL}"
          )
      }
      requests.post(WEBHOOK_URL, json=fallback_message)

    # บันทึกสถานะปัจจุบันลงไฟล์
    with open(STATE_FILE, "w", encoding="utf-8") as f:
      f.write(current_content)


if __name__ == "__main__":
  main()
