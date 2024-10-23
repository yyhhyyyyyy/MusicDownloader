import os

from pydub import AudioSegment

from music_download import ensure_directories_exist


class MusicCover:
    def __init__(self, save_path="./download_dir", cover_mp3_dir="./cover_mp3_dir"):
        self.save_path = save_path
        self.cover_mp3_dir = cover_mp3_dir
        ensure_directories_exist(self.cover_mp3_dir)

    def cover_mp3(self, format_files="m4a"):
        for filename in os.listdir(self.save_path):
            if filename.endswith(".m4a"):
                m4a_file = os.path.join(self.save_path, filename)
                audio = AudioSegment.from_file(m4a_file, format=format_files)
                mp3_file = os.path.join(
                    self.cover_mp3_dir, os.path.splitext(filename)[0] + ".mp3"
                )
                audio.export(mp3_file, format="mp3")
                print(f"已转换: {filename} -> {mp3_file}")
        print("所有文件转换完成！")

    def run(self, format_files):
        self.cover_mp3(format_files)


if __name__ == "__main__":
    cover = MusicCover()
    cover.run()
