import json
import smtplib
import ssl
from http.server import BaseHTTPRequestHandler
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # --- 1. قراءة البيانات من الطلب ---
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data)

            recipient_email = data.get('recipient')
            subject = data.get('subject')
            body = data.get('body')

            if not all([recipient_email, subject, body]):
                self._send_response(400, {'message': 'خطأ: جميع الحقول مطلوبة.'})
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
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))
