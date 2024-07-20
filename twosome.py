from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from datetime import datetime
import time
import json

# 현재 날짜 가져오기
current_date = datetime.now().strftime("%Y-%m-%d")
folder_path = "twosome"
filename = f"{folder_path}/twosome_{current_date}.json"

# 웹드라이버 설치
options = ChromeOptions()
options.add_argument("--headless")
service = ChromeService(executable_path=ChromeDriverManager().install())
browser = webdriver.Chrome(service=service, options=options)

browser.get('https://mo.twosome.co.kr/so/storeSearch.do')

# 페이지가 완전히 로드될 때까지 대기
WebDriverWait(browser, 10).until(
    EC.element_to_be_clickable((By.CLASS_NAME, "search_shop"))
)

search_box = browser.find_element(By.CSS_SELECTOR, ".search_shop > span > input:nth-child(2)")
search_box.send_keys('dt점')
browser.find_element(By.CSS_SELECTOR, ".search_shop > span > input:nth-child(4)").click()
time.sleep(1)

# 페이지의 끝까지 스크롤 내리기
print("스크롤 내리는 중...")
browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")

# 업데이트된 페이지 소스를 변수에 저장
html_source_updated = browser.page_source
soup = BeautifulSoup(html_source_updated, 'html.parser')

# 데이터 추출
print("데이터 찾는 중...")
ts_data = []
tracks = soup.select(".wrapper.sub > div > div > form > fieldset > .search_shop_result > ul > li")
for track in tracks:
    try:
        title_element = track.find("div", class_="shop_box cf").find("a").find("dl").find("dt").find("strong")
        title = title_element.text.strip() if title_element else ""
        
        address_element = track.find("div", class_="shop_box cf").find("a").find("dl").find("dd")
        address = address_element.text.strip() if address_element else ""
        
        image_url = track.select_one("div.shop_box.cf > div > img").get('src')
        if '=160' in image_url:
            image_url = image_url.replace('=160', '=720')
        
        ts_data.append({
            "title": title,
            "address": address,
            "image": image_url
        })

    except Exception as e:
        print(f"데이터 추출 오류: {e}")

# 데이터를 JSON 파일로 저장
print("데이터 저장 중...")
with open(filename, 'w', encoding='utf-8') as f:
    json.dump(ts_data, f, ensure_ascii=False, indent=4)

# 브라우저 종료
browser.quit()
