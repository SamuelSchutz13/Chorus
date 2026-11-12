"""Scraper com Scrapling: Genius (busca, letra, traduções), Letras.mus.br (letra reserva) e Cifra Club (cifra). Uso:
  python genius.py search "<nome da música>"  -> JSON com resultados
  python genius.py song <id>                  -> JSON com letra e onde ouvir
  python genius.py chords "<artista>" "<música>" -> JSON com a cifra
"""
import json
import logging
import re
import sys
import unicodedata
from urllib.parse import quote_plus

from scrapling.fetchers import Fetcher
from scrapling.parser import Selector

logging.disable(logging.INFO)  # stdout precisa ser só o JSON


def search(q):
    data = Fetcher.get(f"https://genius.com/api/search/multi?q={quote_plus(q)}").json()
    hits = next((s["hits"] for s in data["response"]["sections"] if s["type"] == "song"), [])
    return [
        {
            "id": h["result"]["id"],
            "title": h["result"]["title"],
            "artist": h["result"]["primary_artist"]["name"],
            "image": h["result"]["song_art_image_thumbnail_url"],
        }
        for h in hits
    ]


def extract_lyrics(html):
    page = Selector(html)
    blocks = "".join(e.html_content for e in page.css('div[data-lyrics-container="true"]'))
    if not blocks:
        return None
    doc = Selector(re.sub(r"<br\s*/?>", "\n", blocks))
    # o cabeçalho "Contributors/Translations" fica dentro do container, marcado com data-exclude-from-selection
    text = "".join(doc.xpath("//text()[not(ancestor::*[@data-exclude-from-selection])]").getall())
    return text.strip()


def artist_songs(artist_id):
    data = Fetcher.get(f"https://genius.com/api/artists/{artist_id}/songs?sort=popularity&per_page=12").json()
    return [
        {"id": s["id"], "title": s["title"], "artist": s["primary_artist"]["name"], "image": s["song_art_image_thumbnail_url"]}
        for s in data["response"]["songs"]
    ]


def norm(s):
    s = unicodedata.normalize("NFKD", re.sub(r"\(.*?\)", "", s)).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]", "", s.lower())


def studiosol_search(base, artist, title, title_key, artist_key):
    """Busca do Letras/Cifra Club (mesma empresa, mesmo motor solr). Só aceita o mesmo título; prefere o mesmo artista."""
    q = re.sub(r"[^\w\s]", " ", f"{artist} {title}")  # "&" e afins atrapalham o solr e somem com o resultado certo
    body = Fetcher.get(f"{base}?q={quote_plus(q)}&wt=json&rows=10").body.decode("utf-8")
    m = re.search(r"\((.*)\)", body, re.S)  # resposta vem como JSONP: callback({...})
    if not m:
        return None
    docs = json.loads(m.group(1))["response"]["docs"]
    # t == "2" é música (os outros tipos são álbum, artigo...)
    songs = [d for d in docs if d.get("t") == "2" and norm(d[title_key]) == norm(title)]
    songs.sort(key=lambda d: (bool(d.get("extra_txt")), -d.get("h", 0)))  # versão sem "part./ao vivo" e mais acessada primeiro
    same_artist = [d for d in songs if norm(d[artist_key]) == norm(artist)]
    return (same_artist or songs or [None])[0]


def html_to_text(html):
    html = re.sub(r"<br\s*/?>", "\n", html)
    html = re.sub(r"</p>", "\n\n", html)
    return "".join(Selector(html).xpath("//text()").getall()).strip()


def letras_lyrics(artist, title):
    doc = studiosol_search("https://solr.sscdn.co/letras/m1/", artist, title, "txt", "art")
    if not doc:
        return None
    url = f"https://www.letras.mus.br/{doc['dns']}/{doc['url']}/"
    el = Fetcher.get(url).css(".lyric-original")
    return (html_to_text(el[0].html_content), url) if el else None


def chords(artist, title):
    doc = studiosol_search("https://solr.sscdn.co/cc/h2/", artist, title, "m", "a")
    if not doc:
        return {"chords": None}
    url = f"https://www.cifraclub.com.br/{doc['d']}/{doc['u']}/"
    pre = Fetcher.get(url).css("pre")
    if not pre:
        return {"chords": None}
    # acordes viram NOME (caracteres de uso privado) para o front destacar sem mandar HTML
    html = re.sub(
        r'<b[^>]*data-chord-name="([^"]*)"[^>]*>.*?</b>',
        lambda m: "" + m.group(1) + "",
        pre[0].html_content,
    )
    text = "".join(Selector(html).xpath("//text()").getall()).replace("​", "")
    return {"chords": text.strip("\n"), "url": url}


def song(song_id):
    s = Fetcher.get(f"https://genius.com/api/songs/{song_id}?text_format=plain").json()["response"]["song"]
    description = (s.get("description") or {}).get("plain", "").strip()
    links = [{"provider": m["provider"], "url": m["url"]} for m in s.get("media", [])]
    if s.get("apple_music_id"):
        links.append({"provider": "apple music", "url": f"https://music.apple.com/song/{s['apple_music_id']}"})
    term = quote_plus(f"{s['primary_artist']['name']} {s['title']}")
    found = {l["provider"] for l in links}
    for provider, url in [
        ("spotify", f"https://open.spotify.com/search/{term}"),
        ("youtube", f"https://www.youtube.com/results?search_query={term}"),
        ("deezer", f"https://www.deezer.com/search/{term}"),
    ]:
        if provider not in found:
            links.append({"provider": provider, "url": url, "search": True})
    lyrics, lyrics_url = extract_lyrics(Fetcher.get(s["url"]).html_content), s["url"]
    if not lyrics:
        lyrics, lyrics_url = letras_lyrics(s["primary_artist"]["name"], s["title"]) or (None, None)
    return {
        "title": s["title"],
        "artist": s["primary_artist"]["name"],
        "artistId": s["primary_artist"]["id"],
        "album": (s.get("album") or {}).get("name"),
        "image": s["song_art_image_url"],
        "geniusUrl": s["url"],
        "language": s.get("language"),
        "releaseDate": s.get("release_date"),  # YYYY-MM-DD ou None
        "writers": [a["name"] for a in s.get("writer_artists", [])],
        "producers": [a["name"] for a in s.get("producer_artists", [])],
        "description": None if description in ("", "?") else description,  # Genius usa "?" quando não há descrição
        "translations": [{"id": t["id"], "language": t["language"]} for t in s.get("translation_songs", [])],
        "links": links,
        "lyrics": lyrics,
        "lyricsUrl": lyrics_url,
    }


if __name__ == "__main__":
    cmd, *args = sys.argv[1:]
    result = {"search": search, "song": lambda i: song(int(i)), "chords": chords, "artist": lambda i: artist_songs(int(i))}[cmd](*args)
    sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))
