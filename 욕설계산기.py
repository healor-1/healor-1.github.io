import requests
from bs4 import BeautifulSoup
import re

# 욕설 단어 리스트 확장 및 정규 표현식 패턴 생성
bad_words = [
    '씨발', '개씨발', '새끼', '애미', '좆', '지랄', '병신', '느금', '존나', '개새', '씹', 
    '미친', '썅', '닥쳐', '꺼져', '엿', '좃', '븅신', '쓰발', '쉬발', '개새끼', '개색기', 
    '개새꺄', '썅년', '썅놈', '빡대가리', '돌대가리', '병1신', '병신같은', '좆같은', '뻑큐',
    '느금마', '느그엄', '엠창', '애미뒤짐', '느그아빠', '씨부랄', '빠큐', '오라질'
]
bad_word_patterns = [re.compile(bad_word.replace('1', '[1il]').replace('!', '[1il]'), re.IGNORECASE) for bad_word in bad_words]

def count_bad_words(title, bad_word_patterns):
    return sum(len(pattern.findall(title)) for pattern in bad_word_patterns)

def get_titles_from_gallery(page_url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(page_url, headers=headers)
        response.raise_for_status()  # Raise HTTPError for bad responses
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        return []
    except requests.exceptions.RequestException as req_err:
        print(f"Request error occurred: {req_err}")
        return []

    soup = BeautifulSoup(response.content, 'html.parser', from_encoding='utf-8')

    titles = []
    for row in soup.select('tr.ub-content'):
        title_tag = row.select_one('td.gall_tit a')
        if title_tag:
            titles.append(title_tag.get_text().strip())
    
    if not titles:
        print(f"No titles found on page: {page_url}")
    
    return titles

# 디씨인사이드 공인인증서 갤러리 URL
gallery_url = 'https://gall.dcinside.com/mgallery/board/lists/?id=kica&page='

titles = []
for page in range(1, 27):  # Fetching first 26 pages
    page_url = f"{gallery_url}{page}"
    titles.extend(get_titles_from_gallery(page_url))

# Calculate bad word ratio
total_bad_words = sum(count_bad_words(title, bad_word_patterns) for title in titles)
total_words = sum(len(title.split()) for title in titles)
bad_word_ratio = total_bad_words / total_words if total_words > 0 else 0
non_bad_word_ratio = 1 - bad_word_ratio

# Print results
print(f"수집된 제목 수: {len(titles)}")
print(f"욕설 단어 총 개수: {total_bad_words}")
print(f"총 단어 수: {total_words}")
print(f"욕설이 포함된 비율: {bad_word_ratio * 100:.2f}%")
print(f"욕설이 포함되지 않은 비율: {non_bad_word_ratio * 100:.2f}%")

# Print titles
if titles:
    print(f"첫 5개의 제목: {titles[:5]}")
if total_bad_words > 0:
    bad_word_titles = [title for title in titles if count_bad_words(title, bad_word_patterns) > 0]
    print(f"욕설이 포함된 첫 5개의 제목: {bad_word_titles[:5]}")

# Save titles to a file for review
with open('titles.txt', 'w', encoding='utf-8') as f:
    for title in titles:
        f.write(f"{title}\n")

with open('bad_word_titles.txt', 'w', encoding='utf-8') as f:
    if total_bad_words > 0:
        for title in bad_word_titles:
            f.write(f"{title}\n")

print("게시물 제목이 'titles.txt' 파일에 저장되었습니다.")
print("욕설이 포함된 제목이 'bad_word_titles.txt' 파일에 저장되었습니다.")
