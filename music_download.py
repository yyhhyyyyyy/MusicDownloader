import os
import re

from DrissionPage import Chromium, SessionPage


class MusicDownloader:
    def __init__(self, save_path="./download_dir"):
        self.save_path = save_path
        self.tab = Chromium().latest_tab
        self.ensure_directories_exist(self.save_path)

    def ensure_directories_exist(self, path):
        if not os.path.exists(path):
            os.makedirs(path)
            print(f"已创建文件夹: {path}")

    def login(self):
        self.tab.get("https://feelingmusic.life/")
        if self.tab.ele("#song_name"):
            return
        self.tab.wait.ele_displayed(".auth-button")
        connect = self.tab.ele(".auth-button")
        connect.click()
        self.tab.wait.ele_displayed("text=允许")
        yes = self.tab.ele("text=允许")
        yes.click()

    def download(self, url, song_name, singer):
        page = SessionPage()
        res = page.download(url, self.save_path)
        if res[0] == "success":
            original_file_path = res[1]
            file_extension = os.path.splitext(original_file_path)[1]
            new_file_name = f"{song_name}-{singer}{file_extension}"
            new_file_path = os.path.join(self.save_path, new_file_name)
            if os.path.exists(new_file_path):
                print(f"文件已存在: {new_file_name}")
                os.remove(original_file_path)
                return
            os.rename(original_file_path, new_file_path)
            print(f"已重命名: {new_file_name}")

    def process_music_result(self, music):
        self.tab.listen.start(targets="ws.stream.qqmusic.qq.com")
        song_name = music.children()[1].child(index=1).text
        singer = music.children()[1].child(index=2).text.split("歌手: ")[-1]
        music.child().click()
        quality_menu = self.tab.ele("#quality-menu")
        quality_map = {"FLAC": "/F", "320": "/M8", "128": "/M5", "M4A": "/C4"}
        for quality, target in quality_map.items():
            if quality_menu.ele(f"text={quality}"):
                print(quality, target)
                self.tab.listen.start(targets=f"ws.stream.qqmusic.qq.com{target}")
                quality_menu.ele(f"text={quality}").click()
                break
        for packet in self.tab.listen.steps(count=1):
            self.download(packet.url, song_name, singer)
            break

    def search(self, music_name):
        self.tab.get(f"https://feelingmusic.life/results?Feelinglike={music_name}")
        try:
            music = self.tab.ele("#results", timeout=2).child()
        except Exception:
            music = None

        if music:
            self.process_music_result(music)
        else:
            try:
                self.tab.ele("text=🎵").click()
                self.tab.wait.ele_displayed("#results")
                music = self.tab.ele("#results", timeout=2).child()
                self.process_music_result(music)
            except Exception:
                print(f"未找到歌曲: {music_name}")

    def read_song_names(self, file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            songs = [line.strip() for line in file.readlines()]
        return songs

    def get_downloaded_songs(self):
        downloaded_files = os.listdir(self.save_path)
        downloaded_songs = []
        for file in downloaded_files:
            song_name = os.path.splitext(file)[0]
            cleaned_name = re.sub(r"[^\w\s]", "", song_name)
            downloaded_songs.append(cleaned_name.lower())
        return downloaded_songs

    def filter_downloaded_songs(self, songs):
        downloaded_songs = self.get_downloaded_songs()
        filtered_songs = []
        for song in songs:
            cleaned_song = re.sub(r"[^\w\s]", "", song).lower()
            if not any(cleaned_song in downloaded for downloaded in downloaded_songs):
                filtered_songs.append(song)
        return filtered_songs

    def run(self, songs_file="./songs"):
        songs = self.read_song_names(songs_file)
        songs = self.filter_downloaded_songs(songs)
        if not songs:
            print("所有歌曲都已下载！")
            return
        self.login()
        self.tab.wait(3)
        for song in songs:
            self.search(song)


if __name__ == "__main__":
    downloader = MusicDownloader()
    downloader.run()
