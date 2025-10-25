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
            # --- 1. قراءة البيانات من رابط URL ---
            parsed_path = urlparse(self.path)
            query_params = parse_qs(parsed_path.query)

            # استخلاص البيانات من الرابط
            # Vercel سيقوم بتحويل الأجزاء الديناميكية من الرابط إلى query parameters
            recipient_email = query_params.get('recipient', [None])[0]
            subject = query_params.get('subject', [None])[0]
            body = query_params.get('body', [None])[0]

            if not all([recipient_email, subject, body]):
                self._send_response(400, {'message': 'خطأ: جميع الحقول مطلوبة في الرابط.'})
                return

            # --- 2. إعدادات البريد الإلكتروني (بيانات الاعتماد مكتوبة مباشرة هنا) ---
            sender_email = "appasis444@gmail.com"
            sender_password = "badgfxczucaofogf"  # كلمة مرور التطبيق
            smtp_server = "smtp.gmail.com"
            smtp_port = 587

            # --- 3. إنشاء وإرسال الرسالة ---
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

            # --- 4. إرسال رد النجاح ---
            self._send_response(200, {'message': '✅ تم إرسال البريد الإلكتروني بنجاح!'})

        except Exception as e:
            # --- 5. إرسال رد الفشل في حالة حدوث خطأ ---
            self._send_response(500, {'message': f'فشل إرسال البريد الإلكتروني: {str(e)}'})

    def _send_response(self, status_code, data):
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))