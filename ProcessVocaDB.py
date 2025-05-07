import csv
import datetime
import sys
import json

with open(str(sys.argv[1]), 'r', encoding="utf8") as file:
    inputs = json.load(file)

filename = str(sys.argv[2])

withLyricsCount = 0
withTransl = 0
noLyricsCount = 0
notJp = 0

# Input JSON is a dictionary of dictionaries
# The relevant parts of each dictionary are:
# -- "publishDate": day when this song was first published
# -- "name": name of the song
# -- "artistString": author of the song
# -- "name": name of the song
# -- "lyrics": its own dictionary that holds all lyrical information:
# ---- "translationType": Whether this is original Japanese, Romanized, or English
# ---- "value": Actual textual lyrics (!!!)

with open(filename + '.csv', 'w+', encoding="utf-8-sig") as f:
    # Setup csv
    writer = csv.writer(f, delimiter='|')
    writer.writerow(["ID", "Song Name", "Author Name", "Publish Date",
                     "English Lyrics", "Japanese Lyrics", "Rating"])

    allKata = []
    allRows = []

    for (page) in inputs.get("pages"):
        for (song) in page.get("items"):
            # Remove data that has no lyrical information
            lyrics = song.get("lyrics")
            if len(lyrics) > 0:
                withLyricsCount = withLyricsCount + 1
            else:
                noLyricsCount = noLyricsCount + 1
                continue

            # Gather and clean metadata
            publishDate = datetime.datetime.strptime(str(song.get("publishDate")), '%Y-%m-%dT%H:%M:%SZ')
            artist = str(song.get("artistString"))
            song_id = int(song.get("id"))
            rating = int(song.get("ratingScore"))
            jpLyrics = ""
            enLyrics = ""
            isJapaneseSong = True

            for (lyricChunk) in lyrics:
                if not isJapaneseSong:
                    continue
                lyricsInJp = False
                lyricsInEn = False
                # Print only Japanese-original lyrics
                translationType = str(lyricChunk.get("translationType"))
                if translationType.lower() == "Original".lower():
                    lyricsInJp = "ja" in lyricChunk.get("cultureCodes")
                    lyricsInJp = lyricsInJp | ("oin" in lyricChunk.get("cultureCodes"))
                    lyricsInJp = lyricsInJp | ("ojp" in lyricChunk.get("cultureCodes"))
                    if not lyricsInJp:
                        notJp = notJp + 1
                        isJapaneseSong = False
                        #print("Not japanese song; skipping")
                        continue
                    #else:
                        #print("found japanese song")
                elif translationType.lower() == "Translation".lower():
                    lyricsInEn = "en" in lyricChunk.get("cultureCodes")
                    if not lyricsInEn:
                        #print("found translation, but not in english")
                        continue
                    #else:
                        #print("found en translation")
                else:
                    #print("found neither original nor translation")
                    continue

                thisLyrics = str(lyricChunk.get("value"))
                if len(thisLyrics) < 10:
                    #print("Lyrics not long enough; skipping")
                    continue
                if lyricsInJp:
                    #print(f"Jp lyrics are {len(thisLyrics)} char long")
                    jpLyrics = thisLyrics
                elif lyricsInEn:
                    #print(f"en tl is {len(thisLyrics)} char long")
                    enLyrics = thisLyrics

            if isJapaneseSong and len(jpLyrics) > 10:
                #print("saved new song")
                fullList = [song_id, str(song.get("name")), artist,
                            publishDate, enLyrics, jpLyrics, rating]
                if len(enLyrics) > 10:
                    withTransl += 1
                writer.writerow(fullList)

    # Print final counts
    print("\nFinal song count: " + str(withLyricsCount) + "\n")
    print(f"{float(withTransl) / withLyricsCount} percent of songs had translations\n")
    print(f"{float(withLyricsCount) / (withLyricsCount + noLyricsCount)} percent of songs had lyrics\n")
    print("Removed " + str(notJp) + " non-Japanese songs\n")

