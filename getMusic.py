import json
import time
import urllib.parse
import urllib.request


def fetchSongLyrics(songId):
    # API công khai của Zing MP3 để lấy file lời bài hát
    lyricApiUrl = f"https://api.mp3.zing.vn/api/v1/lyric/get?id={songId}"
    try:
        req = urllib.request.Request(
            lyricApiUrl, headers={"User-Agent": "Mozilla/5.0"}
        )
        response = urllib.request.urlopen(req)
        lyricData = json.loads(response.read().decode("utf-8"))

        # Nếu bài hát có lời, tiến hành trích xuất
        if (
            "data" in lyricData
            and len(lyricData["data"]) > 0
            and "content" in lyricData["data"][0]
        ):
            return lyricData["data"][0]["content"]
    except Exception:
        pass
    return "Lời bài hát đang được cập nhật..."


def runMusicScraper():
    keywordFilePath = "searchKeywords.txt"
    databaseFilePath = "albums.json"

    try:
        with open(keywordFilePath, "r", encoding="utf-8") as file:
            songRequests = [
                line.strip() for line in file.readlines() if line.strip()
            ]
    except FileNotFoundError:
        print(f"❌ Không tìm thấy file {keywordFilePath}")
        return

    try:
        with open(databaseFilePath, "r", encoding="utf-8") as file:
            currentDatabase = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        currentDatabase = []

    existingIds = {song.get("id") for song in currentDatabase if "id" in song}
    newSongsAdded = 0

    print(f"🚀 Bắt đầu quét {len(songRequests)} bài hát kèm lyrics...")

    for songName in songRequests:
        encodedQuery = urllib.parse.quote(songName)
        apiUrl = f"http://ac.mp3.zing.vn/complete?type=artist,song,key,code&num=3&query={encodedQuery}"

        try:
            req = urllib.request.Request(
                apiUrl, headers={"User-Agent": "Mozilla/5.0"}
            )
            apiResponse = urllib.request.urlopen(req)
            jsonData = json.loads(apiResponse.read().decode("utf-8"))

            if "data" in jsonData and len(jsonData["data"]) > 0:
                firstDataBlock = jsonData["data"][0]
                if "song" in firstDataBlock and len(firstDataBlock["song"]) > 0:
                    bestMatch = firstDataBlock["song"][0]
                    songId = bestMatch.get("id")

                    if not songId:
                        continue

                    if songId in existingIds:
                        continue

                    songTitle = bestMatch.get("name", songName)
                    # Phòng thủ KeyError bằng cách tìm cả "artist" lẫn "artists_names"
                    artistName = bestMatch.get(
                        "artist",
                        bestMatch.get("artists_names", "Nhiều ca sĩ"),
                    )

                    coverImage = ""
                    if "thumb" in bestMatch:
                        coverImage = f"https://photo-resize-zmp3.zmdcdn.me/w240_r1x1_jpeg/{bestMatch['thumb']}"

                    # Robot tự động đi lấy thêm lời bài hát dựa vào songId
                    songLyrics = fetchSongLyrics(songId)

                    newSong = {
                        "id": songId,
                        "title": songTitle,
                        "artist": artistName,
                        "coverUrl": coverImage,
                        "audioUrl": f"https://api.mp3.zing.vn/api/streaming/audio/{songId}/128",
                        "lyrics": songLyrics,
                    }

                    currentDatabase.append(newSong)
                    existingIds.add(songId)
                    newSongsAdded += 1
                    print(
                        f"✔️ Đã tìm thấy bài hát và lyrics: {songTitle} - {artistName}"
                    )

            time.sleep(1)

        except Exception as error:
            print(f"❌ Lỗi khi tìm bài '{songName}': {error}")

    if newSongsAdded > 0:
        with open(databaseFilePath, "w", encoding="utf-8") as file:
            json.dump(currentDatabase, file, indent=4, ensure_ascii=False)
        print(
            f"\n✅ Hoàn thành! Đã cập nhật thêm {newSongsAdded} bài hát kèm lyrics."
        )
    else:
        print("\n⚡ Không có bài hát mới nào được thêm vào hệ thống.")


if __name__ == "__main__":
    runMusicScraper()
