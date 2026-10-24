import re
from bs4 import BeautifulSoup
import requests


def generate_m3u():
  url = 'https://rabbitmeow.live/sports'
  headers = {
      'User-Agent': (
          'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
          ' (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
      )
  }

  try:
    print(f'Fetching data from {url}...')
    response = requests.get(url, headers=headers, timeout=15)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')

    m3u_content = '#EXTM3U x-tvg-url=""\n'
    channels_found = 0

    for a_tag in soup.find_all('a', href=True):
      link = a_tag['href']
      title = a_tag.get_text(strip=True)

      if title and link:
        if link.startswith('/'):
          link = f'https://rabbitmeow.live{link}'
        elif not link.startswith('http'):
          continue

        clean_title = re.sub(r'[\r\n\t]', ' ', title)
        clean_title = re.sub(r'\s+', ' ', clean_title).strip()

        if len(clean_title) > 2:
          m3u_content += (
              f'#EXTINF:-1 tvg-logo="" group-title="Live Sports",'
              f' {clean_title}\n'
          )
          m3u_content += f'{link}\n'
          channels_found += 1

    with open('playlist.m3u', 'w', encoding='utf-8') as f:
      f.write(m3u_content)

    print(f'Success! Generated playlist.m3u with {channels_found} entries.')

  except Exception as e:
    print(f'Error generating playlist: {e}')
    exit(1)


if __name__ == '__main__':
  generate_m3u()
