# /api/send_email.py

import json
import smtplib
import ssl
from http.server import BaseHTTPRequestHandler
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from urllib.parse import urlparse, parse_qs

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # --- 1. قراءة البريد الإلكتروني المستلم من رابط URL ---
            # يتم تحليل الرابط للحصول على البريد الإلكتروني بعد ?recipient=
            query_components = parse_qs(urlparse(self.path).query)
            recipient_email = query_components.get('recipient', [None])[0]

            # التحقق من وجود البريد الإلكتروني
            if not recipient_email:
                self._send_response(400, {'message': 'خطأ: البريد الإلكتروني للمستلم مطلوب. مثال: /api/send_email?recipient=email@example.com'})
                return

            # --- 2. تعيين الموضوع والمحتوى بشكل ثابت ---
            subject = "رمز التحقق من الموقع"
            body = "رمز التحقق هو 75455"

            # --- 3. إعدادات البريد الإلكتروني (بيانات الاعتماد مكتوبة مباشرة هنا) ---
            # ⚠️ تنبيه أمني: من الأفضل استخدام متغيرات البيئة (Environment Variables) لتخزين بيانات الاعتماد بدلاً من كتابتها مباشرة في الكود.
            sender_email = "appasis444@gmail.com"
            sender_password = "badgfxczucaofogf"  # كلمة مرور التطبيق
            smtp_server = "smtp.gmail.com"
            smtp_port = 587

            # --- 4. إنشاء وإرسال الرسالة ---
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = recipient_email
            msg['Subject'] = subject

            # إضافة محتوى الرسالة
            msg.attach(MIMEText(body, 'plain', 'utf-8'))

            # إرسال البريد
            context = ssl.create_default_context()
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls(context=context)
                server.login(sender_email, sender_password)
                server.sendmail(sender_email, recipient_email, msg.as_string())

            # --- 5. إرسال رد النجاح ---
            self._send_response(200, {'message': f'✅ تم إرسال البريد الإلكتروني بنجاح إلى {recipient_email}!'})

        except Exception as e:
            # --- 6. إرسال رد الفشل في حالة حدوث خطأ ---
            self._send_response(500, {'message': f'فشل إرسال البريد الإلكتروني: {str(e)}'})

    def _send_response(self, status_code, data):
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.end_headers()
        # استخدام ensure_ascii=False لضمان عرض الحروف العربية بشكل صحيح
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))