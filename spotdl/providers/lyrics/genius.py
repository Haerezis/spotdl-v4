from typing import List, Optional

import requests

from bs4 import BeautifulSoup

from spotdl.providers.lyrics.base import LyricsProvider


class Genius(LyricsProvider):
    def get_lyrics(self, name: str, artists: List[str], **_) -> Optional[str]:
        """
        Try to get lyrics from genius
        """

        try:
            headers = {
                "Authorization": "Bearer "
                "alXXDbPZtK1m2RrZ8I4k2Hn8Ahsd0Gh_o076HYvcdlBvmc0ULL1H8Z8xRlew5qaG",
            }

            headers.update(self.headers)

            artist_str = ", ".join(
                artist for artist in artists if artist.lower() not in name.lower()
            )

            search_response = requests.get(
                "https://api.genius.com/search",
                params={"q": f"{name} {artist_str}"},
                headers=headers,
            )

            song_id = search_response.json()["response"]["hits"][0]["result"]["id"]

            song_response = requests.get(
                f"https://api.genius.com/songs/{song_id}", headers=headers
            )

            song_url = song_response.json()["response"]["song"]["url"]
            genius_page_response = requests.get(song_url, headers=headers)
            if not genius_page_response.ok:
                return None

            soup = BeautifulSoup(
                genius_page_response.text.replace("<br/>", "\n"), "html.parser"
            )
            lyrics_div = soup.select_one("div.lyrics")

            if lyrics_div is not None:
                return lyrics_div.get_text().strip()

            lyrics_containers = soup.select("div[class^=Lyrics__Container]")
            lyrics = "\n".join(con.get_text() for con in lyrics_containers)
            return lyrics.strip()
        except Exception:
            return None
