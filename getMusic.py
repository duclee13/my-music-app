import json
import time
import urllib.parse
import urllib.request


def runMusicScraper():
    keywordFilePath = "searchKeywords.txt"
    databaseFilePath = "albums.json"

    # 1. Đọc danh sách từ file txt
    try:
        with open(keywordFilePath, "r", encoding="utf-8") as file:
            songRequests = [
                line.strip() for line in file.readlines() if line.strip()
            ]
    except FileNotFoundError:
        print(f"❌ Không tìm thấy file {keywordFilePath}")
        return

    # 2. Đọc dữ liệu cũ từ albums.json (nếu có)
    try:
        with open(databaseFilePath, "r", encoding="utf-8") as file:
            currentDatabase = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        currentDatabase = []

    existingIds = {song["id"] for song in currentDatabase}
    newSongsAdded = 0

    print(f"🚀 Bắt đầu quét {len(songRequests)} bài hát...")

    # 3. Quét API Zing MP3 để tìm thông tin nhạc sạch
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
                    songId = bestMatch["id"]

                    # Bỏ qua nếu bài hát đã tồn tại trong database
                    if songId in existingIds:
                        continue

                    songTitle = bestMatch["name"]
                    artistName = bestMatch["artist"]

                    coverImage = ""
                    if "thumb" in bestMatch:
                        coverImage = f"https://photo-resize-zmp3.zmdcdn.me/w240_r1x1_jpeg/{bestMatch['thumb']}"

                    newSong = {
                        "id": songId,
                        "title": songTitle,
                        "artist": artistName,
                        "coverUrl": coverImage,
                        "audioUrl": f"https://api.mp3.zing.vn/api/streaming/audio/{songId}/128",
                    }

                    currentDatabase.append(newSong)
                    existingIds.add(songId)
                    newSongsAdded += 1
                    print(f"✔️ Đã tìm thấy: {songTitle} - {artistName}")

            time.sleep(1)

        except Exception as error:
            print(f"❌ Lỗi khi tìm bài '{songName}': {error}")

    # 4. Lưu dữ liệu mới đè vào albums.json
    if newSongsAdded > 0:
        with open(databaseFilePath, "w", encoding="utf-8") as file:
            json.dump(currentDatabase, file, indent=4, ensure_ascii=False)
        print(
            f"\n✅ Hoàn thành! Đã cập nhật thêm {newSongsAdded} bài hát mới."
        )
    else:
        print("\n⚡ Không có bài hát mới nào được thêm vào hệ thống.")


if __name__ == "__main__":
    runMusicScraper()
