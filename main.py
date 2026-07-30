import os
import threading
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.clock import Clock

class DownloaderApp(App):
    def build(self):
        self.title = "YouTube Course Downloader"
        layout = BoxLayout(orientation='vertical', padding=30, spacing=20)

        self.title_label = Label(text="تحميل كورس يوتيوب مع الترجمة", font_size=20, size_hint_y=None, height=40)
        layout.add_widget(self.title_label)

        self.url_input = TextInput(text='', hint_text='أدخل رابط الـ Playlist هنا...', size_hint_y=None, height=50, multiline=False)
        layout.add_widget(self.url_input)

        self.download_btn = Button(text='ابدأ التحميل الآن', size_hint_y=None, height=60, background_color=(0.1, 0.6, 0.3, 1))
        self.download_btn.bind(on_press=self.start_download_thread)
        layout.add_widget(self.download_btn)

        self.status_label = Label(text='الحالة: جاهز للعمل', font_size=16)
        layout.add_widget(self.status_label)
        return layout

    def update_status(self, text):
        self.status_label.text = text

    def start_download_thread(self, instance):
        url = self.url_input.text.strip()
        if not url:
            self.update_status("خطأ: يرجى إدخال الرابط أولاً!")
            return
        self.download_btn.disabled = True
        self.update_status("جاري بدء التحميل في الخلفية...")
        threading.Thread(target=self.run_downloader, args=(url,)).start()

    def run_downloader(self, url):
        try:
            base_dir = "/storage/emulated/0/جديد /course/"
            os.makedirs(base_dir, exist_ok=True)
            os.chdir(base_dir)
            import subprocess
            cmd = [
                "yt-dlp",
                "-f", "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080][ext=mp4]/best",
                "-o", "video %(playlist_index)s/%(title)s.%(ext)s",
                "--write-subs",
                "--write-auto-subs",
                "--sub-langs", "en",
                "--sub-format", "srt",
                "--force-ipv4",
                "--sleep-requests", "2",
                url
            ]
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, encoding='utf-8')
            for line in process.stdout:
                if '[download]' in line:
                    Clock.schedule_once(lambda dt, l=line: self.update_status(l.strip()), 0)
            process.wait()
            Clock.schedule_once(lambda dt: self.finish_download(), 0)
        except Exception as e:
            Clock.schedule_once(lambda dt, err=str(e): self.update_status(f"حدث خطأ: {err}"), 0)

    def finish_download(self):
        self.download_btn.disabled = False
        self.update_status("تم الانتهاء بنجاح! تحقق من مجلد course.")

if __name__ == '__main__':
    DownloaderApp().run()
