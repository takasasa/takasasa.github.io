import json
from serpapi import GoogleSearch
import os
from dotenv import load_dotenv
from datetime import datetime

# APIキーの取得を場合分け
API_KEY = os.getenv("API_KEY")  # GitHub Actionsで渡される環境変数を使用
if not API_KEY:
    raise ValueError("API_KEYが環境変数から取得できません。")

SCHOLAR_ID = "vUrJ74IAAAAJ"

# (0) 過去に取得したジャーナルリスト（L1）を読み込む
L1_FILE = "data/journal_list.json"
if os.path.exists(L1_FILE):
    with open(L1_FILE, "r", encoding="utf-8") as f:
        L1 = json.load(f)
else:
    L1 = []

# (1) 現在のすべてのジャーナルリスト（L2）を取得する
params = {
    "engine": "google_scholar_author",
    "author_id": SCHOLAR_ID,
    "api_key": API_KEY,
    "num": 100,
    "no_truncation": "true",
    "sort": "pub_date",
    "start": 0,
    "hl": "ja"
}

L2 = []
next_page_token = None

while True:
    try:
        if next_page_token:
            params["start"] = next_page_token
        search = GoogleSearch(params)
        results = search.get_dict()
    except Exception as e:
        print(f"APIエラー: {e}")
        continue  # 次の処理に進む
    fetched_articles = results.get("articles", [])
    if not fetched_articles:
        break
    L2.extend(fetched_articles)
    next_page_token = results.get("next_page_token")
    if not next_page_token:
        break

# (2) L1とL2を比較して、タイトルの追加を確認、追加分をL3とする
existing_titles = {article["title"] for article in L1}
L3 = [article for article in L2 if article["title"] not in existing_titles]

# (3) L3にリストアップされている記事はすべて詳細情報にアクセスし、L1に追記する
def fetch_article_details(article):
    try:
        citation_id = article.get("citation_id")
        if not citation_id:
            return article
        detail_params = {
            "engine": "google_scholar_author",
            "author_id": SCHOLAR_ID,
            "api_key": API_KEY,
            "view_op": "view_citation",
            "citation_id": citation_id
        }
        search = GoogleSearch(detail_params)
        details = search.get_dict()
        return {**article, **details}
    except Exception as e:
        print(f"詳細情報取得エラー: {e}")
        return article

for article in L3:
    detailed_article = fetch_article_details(article)
    L1.append(detailed_article)

# 更新日を取得
update_date = datetime.now().strftime("%Y/%m/%d")

# 更新日をテキストファイルに出力
if L3:
    with open("data/update_date.txt", "w", encoding="utf-8") as f:
        f.write(update_date)

# (4) 出版日時でソートし、L1を保存する
L1.sort(key=lambda x: x.get("pub_date", x.get("year", "0000")), reverse=True)
with open(L1_FILE, "w", encoding="utf-8") as f:
    json.dump(L1, f, ensure_ascii=False, indent=2)

# (5) L1をもとに分類し、HTML生成する
def classify_article(article):
    citation = article.get("citation", {})
    if "journal" in citation:
        article_type = "journal"
    elif "conference" in citation:
        article_type = "conference"
    else:
        article_type = "unknown"

    authors = citation.get("authors", "")
    publication = citation.get("journal", citation.get("conference", ""))
    is_international = all(
        all(ord(char) < 128 for char in text) for text in [authors, publication]
    )

    international_or_domestic = "international" if is_international else "domestic"

    return {"type": article_type, "category": international_or_domestic, **article}

classified_articles = {"domestic_conference": [], "domestic_journal": [], "international_conference": [], "international_journal": []}

for article in L1:
    classified_article = classify_article(article)
    key = f"{classified_article['category']}_{classified_article['type']}"
    if key not in classified_articles:
        classified_articles[key] = []
    classified_articles[key].append(classified_article)

def generate_html_with_citation(articles):
    def format_field(field_name, value):
        return f"{field_name} {value}" if value != "N/A" else ""

    def format_authors(authors):
        return authors.replace("佐々木崇元", "<b>佐々木崇元</b>").replace("Takayuki Sasaki", "<b>Takayuki Sasaki</b>")

    # HTMLの基本構造を追加
    html = """<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <title>Publication List</title>
</head>
<body>
<ul>
"""
    for pub in articles:
        citation = pub.get("citation", {})
        pub_title = citation.get("title", pub.get("title", "N/A"))
        authors = citation.get("authors", pub.get("authors", "N/A"))
        publication = citation.get("journal", citation.get("conference", "N/A"))
        volume = citation.get("volume", "N/A")
        number = citation.get("issue", "N/A")
        pages = citation.get("pages", "N/A")
        publication_date = pub.get("year", "N/A")

        fields = [
            format_authors(authors),
            f"\"{pub_title}\"" if pub_title != "N/A" else "",
            f"<i>{publication}</i>" if publication != "N/A" else "",
            format_field("vol.", volume),
            format_field("no.", number),
            format_field("pp.", pages),
            publication_date,
        ]

        formatted_fields = [field for field in fields if field]
        html += f"  <li>{', '.join(formatted_fields)}.</li>\n"
    html += "</ul>\n</body>\n</html>"
    return html

domestic_conference_html = generate_html_with_citation(classified_articles["domestic_conference"])
domestic_journal_html = generate_html_with_citation(classified_articles["domestic_journal"])
international_conference_html = generate_html_with_citation(classified_articles["international_conference"])
international_journal_html = generate_html_with_citation(classified_articles["international_journal"])

with open("templates/domestic_conference.html", "w", encoding="utf-8") as f:
    f.write(domestic_conference_html)
print("domestic_conference.htmlを生成しました。")

with open("templates/domestic_journal.html", "w", encoding="utf-8") as f:
    f.write(domestic_journal_html)

with open("templates/international_conference.html", "w", encoding="utf-8") as f:
    f.write(international_conference_html)

with open("templates/international_journal.html", "w", encoding="utf-8") as f:
    f.write(international_journal_html)
