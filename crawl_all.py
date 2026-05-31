import sys, time, uuid, re, json
from datetime import datetime, date, timedelta
from urllib.parse import urljoin

try:
    import httpx
    from bs4 import BeautifulSoup
    import psycopg2
except ImportError:
    print("请先安装: pip install httpx beautifulsoup4 lxml psycopg2-binary")
    sys.exit(1)

DAYS = int(sys.argv[1]) if len(sys.argv) > 1 else 180
cutoff = date.today() - timedelta(days=DAYS)

# 自适应数据库地址：Docker 容器内用 postgres，宿主机用 localhost
import socket as _socket
def _get_db_host():
    try:
        _socket.create_connection(("postgres", 5432), timeout=1)
        return "postgres"
    except:
        return "localhost"

DB = {
    "host": _get_db_host(), "port": 5432,
    "user": "utd24_admin", "password": "utd24_secure_pwd_2024",
    "dbname": "utd24_literature",
}

JOURNALS = [
    ("The Accounting Review", "AR", "0001-4826", "aaahq"),
    ("Journal of Accounting and Economics", "JAE", "0165-4101", "elsevier"),
    ("Journal of Accounting Research", "JAR", "0021-8456", "wiley"),
    ("Journal of Finance", "JF", "0022-1082", "wiley"),
    ("Journal of Financial Economics", "JFE", "0304-405X", "elsevier"),
    ("The Review of Financial Studies", "RFS", "0893-9454", "oxford"),
    ("Information Systems Research", "ISR", "1047-7047", "informs"),
    ("INFORMS Journal on Computing", "JOC", "1091-9856", "informs"),
    ("MIS Quarterly", "MISQ", "0276-7783", "misq"),
    ("Journal of Consumer Research", "JCR", "0093-5301", "oxford"),
    ("Journal of Marketing", "JM", "0022-2429", "sage"),
    ("Journal of Marketing Research", "JMR", "0022-2437", "sage"),
    ("Marketing Science", "MKS", "0732-2399", "informs"),
    ("Management Science", "MS", "0025-1909", "informs"),
    ("Operations Research", "OR", "0030-364X", "informs"),
    ("Journal of Operations Management", "JOM", "0272-6963", "wiley"),
    ("Manufacturing & Service Operations Management", "M&SOM", "1523-4614", "informs"),
    ("Production and Operations Management", "POM", "1059-1478", "sage"),
    ("Academy of Management Journal", "AMJ", "0001-4273", "aom"),
    ("Academy of Management Review", "AMR", "0363-7425", "aom"),
    ("Administrative Science Quarterly", "ASQ", "0001-8392", "sage"),
    ("Organization Science", "OS", "1047-7039", "informs"),
    ("Journal of International Business Studies", "JIBS", "0047-2506", "springer"),
    ("Strategic Management Journal", "SMJ", "0143-2095", "wiley"),
]

HEADERS = {
    "User-Agent": "UTD24-Literature-Platform/2.0 (mailto:research@utd24.local)",
}

CROSSREF_API = "https://api.crossref.org/works"
SEMANTIC_API = "https://api.semanticscholar.org/graph/v1/paper/search"

conn = psycopg2.connect(**DB)
cur = conn.cursor()

# ── 数据库默认值 ──
for tbl in ["articles", "authors", "keywords"]:
    for col in ["created_at"]:
        try: cur.execute(f"ALTER TABLE {tbl} ALTER COLUMN {col} SET DEFAULT NOW()")
        except: pass
conn.commit()

def jid(name):
    cur.execute("SELECT id FROM journals WHERE name = %s", (name,))
    r = cur.fetchone()
    return r[0] if r else None

def article_exists(doi):
    cur.execute("SELECT 1 FROM articles WHERE doi = %s", (doi,))
    return cur.fetchone() is not None

def get_or_create_author(name, country=None, affiliation=None):
    n = re.sub(r'\s+', ' ', name).strip().lower()
    cur.execute("SELECT id FROM authors WHERE normalized_name = %s", (n,))
    r = cur.fetchone()
    if r:
        if country:
            cur.execute("UPDATE authors SET country=%s WHERE id=%s AND country IS NULL", (country, r[0]))
        return r[0]
    aid = str(uuid.uuid4())
    cur.execute("INSERT INTO authors (id,name,normalized_name,country,affiliation,created_at) VALUES (%s,%s,%s,%s,%s,NOW())",
                (aid, name, n, country, affiliation))
    return aid

def get_or_create_keyword(kw):
    nkw = kw.strip().lower()
    cur.execute("SELECT id FROM keywords WHERE normalized_keyword = %s", (nkw,))
    r = cur.fetchone()
    if r:
        return r[0]
    kid = str(uuid.uuid4())
    cur.execute("INSERT INTO keywords (id,keyword,normalized_keyword,created_at) VALUES (%s,%s,%s,NOW())",
                (kid, kw.strip(), nkw))
    return kid

def extract_country(affiliation_list):
    if not affiliation_list:
        return None
    countries_map = {
        "United States": "USA", "China": "China", "United Kingdom": "UK",
        "Canada": "Canada", "Germany": "Germany", "France": "France",
        "Singapore": "Singapore", "Netherlands": "Netherlands",
        "South Korea": "South Korea", "India": "India", "Australia": "Australia",
        "Italy": "Italy", "Spain": "Spain", "Switzerland": "Switzerland",
        "Japan": "Japan", "Sweden": "Sweden", "Denmark": "Denmark",
        "Israel": "Israel", "Taiwan": "China", "Brazil": "Brazil",
        "Belgium": "Belgium", "Norway": "Norway", "Austria": "Austria",
        "Hong Kong": "China", "Finland": "Finland", "Portugal": "Portugal",
    }
    for aff in affiliation_list:
        name = aff.get("name", "") if isinstance(aff, dict) else str(aff)
        for cn, code in countries_map.items():
            if cn.lower() in name.lower():
                return code
        parts = name.split(",")
        for part in parts[-2:]:
            for cn, code in countries_map.items():
                if cn.lower() in part.strip().lower():
                    return code
    return None

# ═══ CrossRef API ═══

def crawl_crossref_paginated(issn, journal_name):
    """CrossRef API 带分页 + ISSN+名称双查"""
    all_items = []
    buffer_date = cutoff - __import__('datetime').timedelta(days=30)
    from_date = buffer_date.strftime("%Y-%m-%d")  # 往前推30天补偿CrossRef日期偏差

    # 策略 1：按 ISSN 查
    for filter_str in [f"issn:{issn}", f"container-title:{journal_name}"]:
        cursor = "*"
        page = 0
        while page < 5:  # 最多 5 页（200*5=1000 条）
            params = {
                "filter": f"{filter_str},from-pub-date:{from_date}",
                "rows": 200,
                "sort": "published",
                "order": "desc",
                "cursor": cursor,
            }
            try:
                resp = httpx.get(CROSSREF_API, params=params, headers=HEADERS, timeout=30)
                if resp.status_code == 200:
                    data = resp.json()
                    items = data.get("message", {}).get("items", [])
                    total_results = data.get("message", {}).get("total-results", 0)
                    all_items.extend(items)
                    print(f"      Page {page+1}: got {len(items)} items (total available: {total_results})")
                    new_cursor = data.get("message", {}).get("next-cursor")
                    if not new_cursor or new_cursor == cursor or len(items) == 0:
                        if new_cursor == cursor:
                            print(f"      End of pagination (cursor unchanged)")
                        break
                    cursor = new_cursor
                    page += 1
                    time.sleep(0.5)
                else:
                    print(f"      CrossRef HTTP {resp.status_code}")
                    break
            except Exception as e:
                print(f"      CrossRef page {page} error: {e}")
                break

    # 去重（按 DOI）
    seen = set()
    unique = []
    for item in all_items:
        doi = item.get("DOI")
        if doi and doi not in seen:
            seen.add(doi)
            unique.append(item)

    print(f"      CrossRef: {len(unique)} unique items (from {len(all_items)} total)")
    return unique

def save_crossref_article(item, journal_id):
    """存入数据库"""
    doi = item.get("DOI")
    if not doi or article_exists(doi):
        return False

    title = (item.get("title") or ["Unknown"])[0][:500]
    abstract = item.get("abstract", "")
    if isinstance(abstract, str):
        abstract = re.sub(r'<[^>]+>', ' ', abstract)
        abstract = re.sub(r'\s+', ' ', abstract).strip()[:5000]

    pub_date = None
    for df in ["published-print", "published-online", "issued", "created"]:
        dp = item.get(df, {})
        if dp and "date-parts" in dp and dp["date-parts"]:
            parts = dp["date-parts"][0]
            try:
                pub_date = date(parts[0], parts[1] if len(parts) > 1 else 1, parts[2] if len(parts) > 2 else 1)
                break
            except: pass
    if pub_date and pub_date < cutoff:
        return False

    volume = str(item.get("volume", "") or "")
    issue = str(item.get("issue", "") or "")
    page = item.get("page", "")

    aid = str(uuid.uuid4())
    try:
        cur.execute("""
            INSERT INTO articles (id,title,abstract,doi,published_date,volume,issue,pages,source_url,source_platform,journal_id,crawled_at,created_at,updated_at)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,NOW(),NOW(),NOW())
        """, (aid, title, abstract, doi, pub_date, volume, issue, page, f"https://doi.org/{doi}", "crossref", journal_id))

        affiliations = []
        for ae in item.get("author", []):
            if "affiliation" in ae:
                affiliations.extend(ae["affiliation"])
        country = extract_country(affiliations)

        for order, ae in enumerate(item.get("author", []), 1):
            full = f"{ae.get('given','')} {ae.get('family','')}".strip()
            if full:
                # 提取该作者的机构名
                aff_parts = []
                for a in (ae.get("affiliation") or []):
                    if isinstance(a, dict) and a.get("name"):
                        aff_parts.append(a["name"][:200])
                aff_name = "; ".join(aff_parts)[:500] if aff_parts else None
                aid2 = get_or_create_author(full, country, aff_name)
                cur.execute("INSERT INTO article_authors (article_id,author_id,author_order) VALUES (%s,%s,%s) ON CONFLICT DO NOTHING", (aid, aid2, order))

        for kw in (item.get("subject") or [])[:10]:
            kid = get_or_create_keyword(kw)
            cur.execute("INSERT INTO article_keywords (article_id,keyword_id) VALUES (%s,%s) ON CONFLICT DO NOTHING", (aid, kid))

        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print(f"        DB error: {e}")
        return False

# ═══ Semantic Scholar (备用) ═══

def crawl_semantic(journal_name, issn):
    """Semantic Scholar API (带偏移翻页)"""
    items = []
    seen_dois = set()
    
    for q in [journal_name, issn]:
        offset = 0
        while offset < 500:  # 最多 5 页 × 100 = 500 条
            params = {
                "query": q,
                "limit": 100,
                "offset": offset,
                "fields": "title,abstract,externalIds,authors,publicationDate,journal,fieldsOfStudy",
            }
            try:
                resp = httpx.get(SEMANTIC_API, params=params, headers=HEADERS, timeout=30)
                if resp.status_code == 200:
                    data = resp.json().get("data", [])
                    if not data:
                        break
                    new_in_page = 0
                    for p in data:
                        doi = (p.get("externalIds") or {}).get("DOI")
                        if doi and doi not in seen_dois:
                            seen_dois.add(doi)
                            pub_date_str = p.get("publicationDate") or "2020-01-01"
                            try:
                                parts = [int(x) for x in pub_date_str.split("-")]
                            except:
                                parts = [2020, 1, 1]
                            items.append({
                                "DOI": doi,
                                "title": [p.get("title", "Unknown")],
                                "abstract": p.get("abstract", ""),
                                "published-print": {"date-parts": [parts]},
                                "author": [{"given": (a.get("name","") or ""), "family": ""} for a in (p.get("authors") or [])],
                                "subject": p.get("fieldsOfStudy") or [],
                                "source": "semantic",
                            })
                            new_in_page += 1
                    offset += 100
                    if new_in_page == 0:
                        break
                    time.sleep(1.5)
                else:
                    break
            except Exception as e:
                print(f"      Semantic Scholar error (offset={offset}): {e}")
                break
    
    print(f"      Semantic Scholar: {len(items)} items (offset-paginated)")
    return items


# ═══ OpenAlex API (第三数据源) ═══
def crawl_openalex(journal_name, issn):
    """OpenAlex API - 免费开放学术数据库"""
    items = []
    url = "https://api.openalex.org/works"
    from_date = cutoff.strftime("%Y-%m-%d")
    
    # 用 ISSN 搜索
    params = {
        "filter": f"primary_location.source.issn:{issn},from_publication_date:{from_date}",
        "sort": "publication_date:desc",
        "per_page": 200,
    }
    
    for page in range(3):
        try:
            resp = httpx.get(url, params=params, headers=HEADERS, timeout=30)
            if resp.status_code == 200:
                data = resp.json()
                results = data.get("results", [])
                for w in results:
                    doi = w.get("doi", "").replace("https://doi.org/", "")
                    if doi and doi not in [i.get("DOI") for i in items]:
                        pub_date_str = w.get("publication_date") or "2020-01-01"
                        try:
                            parts = [int(x) for x in pub_date_str.split("-")]
                        except:
                            parts = [2020, 1, 1]
                        authors_raw = []
                        for a in (w.get("authorships") or []):
                            author_raw = a.get("author", {})
                            authors_raw.append({
                                "given": (author_raw.get("display_name") or "").split()[-1] if author_raw.get("display_name") else "",
                                "family": (author_raw.get("display_name") or "").split()[0] if len((author_raw.get("display_name") or "").split()) > 1 else author_raw.get("display_name", ""),
                            })
                        items.append({
                            "DOI": doi,
                            "title": [w.get("title", "Unknown")],
                            "abstract": "",  # OpenAlex 免费 API 不含摘要
                            "published-print": {"date-parts": [parts]},
                            "author": authors_raw,
                            "subject": [c.get("display_name") for c in (w.get("concepts") or [])[:5]],
                            "source": "openalex",
                        })
                
                # 翻页
                next_cursor = data.get("meta", {}).get("next_cursor")
                if next_cursor:
                    params["cursor"] = next_cursor
                else:
                    break
                time.sleep(0.5)
            else:
                break
        except Exception as e:
            print(f"      OpenAlex error: {e}")
            break
    
    print(f"      OpenAlex: {len(items)} items")
    return items

# ═══ 主流程 ═══

print(f"\n{'='*60}")
print(f"🚀 UTD24 爬虫 v2 — past {DAYS} days")
print(f"{'='*60}")

report = []
grand_new, grand_found = 0, 0

progress_idx = 0
for name, abbr, issn, platform in JOURNALS:
    print(f"\n{'─'*60}")
    print(f"📰 [{abbr}] {name}  (ISSN: {issn})")

    journal_id = jid(name)
    if not journal_id:
        print(f"  ❌ Not in DB")
        report.append((abbr, name, 0, "NOT IN DB"))
        continue

    # 1. CrossRef (主力)
    print(f"  [1] CrossRef API...")
    items = crawl_crossref_paginated(issn, name)
    new1 = sum(1 for it in items if save_crossref_article(it, journal_id))
    print(f"  CrossRef: {new1} new saved")

    # 2. Semantic Scholar (补充)
    print(f"  [2] Semantic Scholar...")
    items2 = crawl_semantic(name, issn)
    new2 = sum(1 for it in items2 if save_crossref_article(it, journal_id))
    print(f"  Semantic Scholar: {new2} new saved")

    # 3. OpenAlex (第三来源)
    print(f"  [3] OpenAlex...")
    items3 = crawl_openalex(name, issn)
    new3 = sum(1 for it in items3 if save_crossref_article(it, journal_id))
    print(f"  OpenAlex: {new3} new saved")

    total_new = new1 + new2 + new3
    grand_new += total_new
    grand_found += len(items) + len(items2)
    report.append((abbr, name, total_new, "OK"))
    progress_idx = JOURNALS.index((name, abbr, issn, platform)) + 1
    print(f"PROGRESS:{progress_idx}/24:{abbr}:{total_new}")
    print(f"  📊 [{abbr}] total new: {total_new}")

    time.sleep(2)

# ── 报告 ──
print(f"\n{'='*60}")
print(f"📊 FINAL REPORT")
print(f"{'='*60}")
print(f"{'Abbr':<8} {'Journal':<50} {'New':>5}")
print(f"{'─'*70}")
for abbr, name, n, status in report:
    flag = "⚠️ " if n == 0 and status == "OK" else "  "
    print(f"{flag}{abbr:<6} {name:<50} {n:>5}")
print(f"{'─'*70}")
print(f"  {'TOTAL':<56} {grand_new:>5}")
print(f"{'='*60}")
print(f"  Items scanned: {grand_found}")
print(f"  New articles:  {grand_new}")
print(f"  Date range:    {cutoff} to {date.today()}")
print(f"{'='*60}")

cur.close()
conn.close()
