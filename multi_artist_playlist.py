

import spotipy
from spotipy.oauth2 import SpotifyOAuth
import base64


# Авторизация
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id="0b2cac95463a4631be17bb8c16f9bcc3",
    client_secret="c53d724a1bc543aa8cc021bda076cf2b",
    redirect_uri="http://127.0.0.1:8888/callback",
    scope="playlist-modify-public"
))

# Ввод артистов
input_artists = input("Enter artist names (comma-separated): ")
artist_names = [name.strip() for name in input_artists.split(",")]

all_track_ids = set()
all_track_names = set()
playlist_name = " + ".join(artist_names)

for artist_name in artist_names:
    results = sp.search(q='artist:' + artist_name, type='artist', limit=1)
    if not results['artists']['items']:
        print(f"❌ Артист '{artist_name}' не найден.")
        continue

    artist = results['artists']['items'][0]
    artist_id = artist['id']
    print(f"✅ Найден: {artist['name']}")

    # Сбор релизов
    album_ids = []
    for t in ['album', 'single', 'compilation']:
        offset = 0
        while True:
            albums = sp.artist_albums(artist_id, album_type=t, limit=50, offset=offset)
            items = albums['items']
            if not items:
                break
            album_ids.extend(album['id'] for album in items)
            offset += 50
    album_ids = list(set(album_ids))

    # Сбор треков
    for album_id in album_ids:
        tracks = sp.album_tracks(album_id)
        for track in tracks['items']:
            name = track['name'].lower().strip()
            if name not in all_track_names:
                all_track_ids.add(track['id'])
                all_track_names.add(name)

print(f"\n📦 Всего уникальных треков: {len(all_track_ids)}")

# Подтверждение
confirm = input("\nСоздать плейлист с этими треками и обложкой? (y/n): ").lower()
if confirm != 'y':
    print("❌ Отмена.")
    exit()

# Создание плейлиста
user_id = sp.me()['id']
description = f"Плейлист из треков: {', '.join(artist_names)}"
playlist = sp.user_playlist_create(user=user_id, name=f"{playlist_name} — Collection", public=True, description=description)

# Добавление треков
track_ids = list(all_track_ids)
for i in range(0, len(track_ids), 100):
    sp.playlist_add_items(playlist_id=playlist['id'], items=track_ids[i:i+100])

print("🖼 Установка обложки...")

# Применение обложки
try:
    with open("cover.jpg", "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read())
        sp.playlist_upload_cover_image(playlist_id=playlist['id'], image_b64=encoded_image)
    print("✅ Обложка установлена.")
except Exception as e:
    print(f"⚠️ Не удалось установить обложку: {e}")

print(f"\n🎵 Плейлист создан: {playlist['external_urls']['spotify']}")
