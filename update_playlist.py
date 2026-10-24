import asyncio
import re
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright


async def main():
  url = 'https://rabbitmeow.live/sports'

  async with async_playwright() as p:
    print('Launching browser...')
    browser = await p.chromium.launch(headless=True)
    page = await browser.new_page(
        user_agent=(
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            ' (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
        )
    )

    print(f'Navigating to {url}...')
    try:
      # Maghintay na mag-load ang pahina
      await page.goto(url, wait_until='networkidle', timeout=60000)
      await page.wait_for_timeout(5000)  # Hintay ng 5 segundo para sa JS components

      html_content = await page.content()
      soup = BeautifulSoup(html_content, 'html.parser')

      m3u_content = '#EXTM3U x-tvg-url=""\n'
      channels_found = 0

      # Kumuha ng mga links at pamagat ng matches
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

          if len(clean_title) > 2 and not clean_title.lower().startswith(
              ('home', 'contact', 'about', 'privacy')
          ):
            m3u_content += (
                f'#EXTINF:-1 tvg-logo="" group-title="Live Sports",'
                f' {clean_title}\n'
            )
            m3u_content += f'{link}\n'
            channels_found += 1

      # I-save sa playlist.m3u
      with open('playlist.m3u', 'w', encoding='utf-8') as f:
        f.write(m3u_content)

      print(f'Done! Found {channels_found} sports links/channels.')

    except Exception as e:
      print(f'Error occurred: {e}')
      # Gumawa ng kahit papuntang fallback playlist para hindi mag-fail ang GitHub workflow
      with open('playlist.m3u', 'w', encoding='utf-8') as f:
        f.write('#EXTM3U\n')
      exit(1)
    finally:
      await browser.close()


if __name__ == '__main__':
  asyncio.run(main())
