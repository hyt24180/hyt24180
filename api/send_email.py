# /api/send_email.py

import json
import smtplib
import ssl
# لم نعد بحاجة لمكتبة random
from http.server import BaseHTTPRequestHandler
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from urllib.parse import urlparse, parse_qs

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # --- 1. قراءة البريد الإلكتروني ورمز التحقق من رابط URL ---
            query_components = parse_qs(urlparse(self.path).query)
            recipient_email = query_components.get('recipient', [None])[0]
            verification_code = query_components.get('code', [None])[0] # قراءة الرمز من الرابط

            # --- 2. التحقق من وجود البريد الإلكتروني والرمز ---
            if not recipient_email or not verification_code:
                self._send_response(400, {
                    'message': 'خطأ: البريد الإلكتروني ورمز التحقق مطلوبان.',
                    'example': '/api/send_email?recipient=email@example.com&code=123456'
                })
                return

            # --- 3. تعيين الموضوع والمحتوى بناءً على البيانات من الرابط ---
            subject = "رمز التحقق هو:"
            body = verification_code  # استخدام الرمز الذي تم تمريره في الرابط

            # --- 4. إعدادات البريد الإلكتروني (بيانات الاعتماد) ---
            sender_email = "appasis444@gmail.com"
            sender_password = "badgfxczucaofogf"
            smtp_server = "smtp.gmail.com"
            smtp_port = 587

            # --- 5. إنشاء وإرسال الرسالة ---
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = recipient_email
            msg['Subject'] = subject

            msg.attach(MIMEText(body, 'plain', 'utf-8'))

            context = ssl.create_default_context()
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls(context=context)
                server.login(sender_email, sender_password)
                server.sendmail(sender_email, recipient_email, msg.as_string())

            # --- 6. إرسال رد النجاح ---
            self._send_response(200, {'message': f'✅ تم إرسال رمز التحقق "{verification_code}" بنجاح إلى {recipient_email}!'})

        except Exception as e:
            # --- 7. إرسال رد الفشل في حالة حدوث خطأ ---
            self._send_response(500, {'message': f'فشل إرسال البريد الإلكتروني: {str(e)}'})

    def _send_response(self, status_code, data):
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))