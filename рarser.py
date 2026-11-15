# language: Python, file: parser.py
import asyncio
import json
import os
import random
import requests
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

# --- ТВОИ ДАННЫЕ ---
AVITO_URL = "https://www.avito.ru/volgograd/avtomobili/bityy-ASgBAgICAUTyCrKKAQ?context=H4sIAAAAAAAA_wEmANn_YToxOntzOjE6InkiO3M6MTY6Im03QW9WczlvTlBxME5jNzUiO32_uUE4JgAAAA&f=ASgBAgICAkTyCrKKAYYUyOYB&localPriority=0&q=%D0%B0%D0%B2%D1%82%D0%BE%D0%BC%D0%BE%D0%B1%D0%B8%D0%BB%D1%8C&radius=1000&searchRadius=1000"
BOT_TOKEN = "8869233395:AAGmQN1kdWZ3XJzhg8H6TC3mSteE5amFels"
CHAT_ID = "8749474667"
SENT_FILE = "sent_links.json"

def load_sent():
    if os.path.exists(SENT_FILE):
        try:
            with open(SENT_FILE, "r", encoding="utf-8") as f: 
                return set(json.load(f))
        except: return set()
    return set()

def save_sent(sent):
    try:
        with open(SENT_FILE, "w", encoding="utf-8") as f: 
            json.dump(list(sent), f, ensure_ascii=False)
    except: pass

def send_photo(photo_url, caption):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    try:
        res = requests.post(url, data={"chat_id": CHAT_ID, "photo": photo_url, "caption": caption, "parse_mode": "HTML"}, timeout=15)
        if res.status_code != 200:
            requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", data={"chat_id": CHAT_ID, "text": caption, "parse_mode": "HTML"})
    except Exception as e:
        print(f"Ошибка отправки: {e}")

async def parse():
    sent = load_sent()
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        try:
            print("Открываю Авито...")
            await page.goto(AVITO_URL, timeout=60000)
            await asyncio.sleep(random.uniform(3, 6))
            
            content = await page.content()
            soup = BeautifulSoup(content, "html.parser")
            
            new_count = 0
            for ad in soup.find_all("a", href=True):
                href = ad["href"]
                if href.startswith("/") and len(href) > 20 and "?" not in href:
                    full_url = f"https://www.avito.ru{href}"
                    if full_url not in sent:
                        title_tag = ad.find("h3") or ad.find("span")
                        title = title_tag.get_text(strip=True) if title_tag else "Объявление"
                        
                        img = ad.find("img")
                        img_url = img["src"] if img and "src" in img.attrs else None
                        if img_url and img_url.startswith("//"): 
                            img_url = "https:" + img_url
                        
                        caption = f"🚨 <b>Новое авто!</b>\n\n<b>{title}</b>\n🔗 <a href='{full_url}'>Открыть</a>"
                        
                        if img_url:
                            send_photo(img_url, caption)
                        else:
                            requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", data={"chat_id": CHAT_ID, "text": caption, "parse_mode": "HTML"})
                        
                        sent.add(full_url)
                        new_count += 1
                        await asyncio.sleep(2)
            
            save_sent(sent)
            print(f"Готово. Новых: {new_count}")
            
        except Exception as e:
            print(f"Ошибка парсинга: {e}")
        finally:
            await browser.close()

async def main():
    while True:
        await parse()
        print("Сплю 10 минут...")
        await asyncio.sleep(600)

if __name__ == "__main__":
    asyncio.run(main())
