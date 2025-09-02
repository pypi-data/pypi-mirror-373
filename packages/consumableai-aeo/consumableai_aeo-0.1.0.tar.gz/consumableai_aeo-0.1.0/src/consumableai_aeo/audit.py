import re
import json
from typing import Dict, Any, List, Optional
import requests
from bs4 import BeautifulSoup

USER_AGENT = "consumableai-aeo/0.1 (+https://www.consumableai.com)"

def _fetch(url: str, timeout: int = 15) -> str:
    resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=timeout)
    resp.raise_for_status()
    return resp.text

def _visible_text(soup: BeautifulSoup) -> str:
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    texts = soup.stripped_strings
    return " ".join(t for t in texts if t)

def _count_syllables(word: str) -> int:
    word = word.lower()
    vowels = "aeiouy"
    count = 0
    prev_vowel = False
    for ch in word:
        is_vowel = ch in vowels
        if is_vowel and not prev_vowel:
            count += 1
        prev_vowel = is_vowel
    if word.endswith("e") and count > 1:
        count -= 1
    return max(1, count)

def _flesch(text: str) -> float:
    sentences = max(1, len(re.findall(r"[.!?]+", text)))
    words = re.findall(r"[a-zA-Z]+", text)
    n_words = max(1, len(words))
    syllables = sum(_count_syllables(w) for w in words) or 1
    return 206.835 - 1.015 * (n_words / sentences) - 84.6 * (syllables / n_words)

def audit_html(html: str, url: Optional[str] = None) -> Dict[str, Any]:
    soup = BeautifulSoup(html, "html.parser")
    title = (soup.title.string or "").strip() if soup.title else ""
    desc_tag = soup.find("meta", attrs={"name": "description"})
    description = (desc_tag.get("content") or "").strip() if desc_tag else ""

    robots_tag = soup.find("meta", attrs={"name": "robots"})
    robots = (robots_tag.get("content") or "").lower().strip() if robots_tag else ""

    canonical_tag = soup.find("link", attrs={"rel": "canonical"})
    canonical = (canonical_tag.get("href") or "").strip() if canonical_tag else ""

    og_title = soup.find("meta", property="og:title")
    og_desc = soup.find("meta", property="og:description")
    twitter_card = soup.find("meta", attrs={"name": "twitter:card"})

    jsonld_types = []
    for s in soup.find_all("script", {"type": "application/ld+json"}):
        try:
            data = json.loads(s.string or "{}")
        except Exception:
            continue
        def collect_types(obj):
            if isinstance(obj, dict):
                t = obj.get("@type")
                if t:
                    if isinstance(t, list):
                        jsonld_types.extend([str(x) for x in t])
                    else:
                        jsonld_types.append(str(t))
                for v in obj.values():
                    collect_types(v)
            elif isinstance(obj, list):
                for it in obj:
                    collect_types(it)
        collect_types(data)

    h1s = [h.get_text(strip=True) for h in soup.find_all("h1")]
    h2s = [h.get_text(strip=True) for h in soup.find_all("h2")]
    imgs = soup.find_all("img")
    total_imgs = len(imgs)
    imgs_with_alt = sum(1 for i in imgs if i.get("alt"))

    text = _visible_text(soup)
    readability = _flesch(text)

    report = {
        "url": url,
        "title": title,
        "title_length": len(title),
        "description": description,
        "description_length": len(description),
        "canonical": canonical,
        "robots": robots,
        "og_title": bool(og_title),
        "og_description": bool(og_desc),
        "twitter_card": twitter_card.get("content") if twitter_card else None,
        "jsonld_types": sorted(set(jsonld_types)),
        "h1_count": len(h1s),
        "h2_count": len(h2s),
        "h1": h1s[0] if h1s else "",
        "images_total": total_imgs,
        "images_with_alt": imgs_with_alt,
        "alt_ratio": (imgs_with_alt / total_imgs) if total_imgs else None,
        "readability_flesch": round(readability, 2),
    }
    report["score"] = score_report(report)
    return report

def score_report(r: Dict[str, Any]) -> Dict[str, Any]:
    score = 0
    signals = {}

    def add(name, pts, cond):
        nonlocal score
        signals[name] = {"points": pts, "earned": pts if cond else 0, "ok": bool(cond)}
        if cond: score += pts

    add("title_present", 5, bool(r["title"]))
    add("title_length_good", 5, 10 <= r["title_length"] <= 60)
    add("description_present", 5, bool(r["description"]))
    add("description_length_good", 5, 50 <= r["description_length"] <= 170)
    add("canonical_present", 10, bool(r["canonical"]))
    add("robots_index_follow", 5, ("noindex" not in (r["robots"] or "")) and ("nofollow" not in (r["robots"] or "")))
    add("og_minimum", 10, r["og_title"] and r["og_description"])
    add("twitter_card", 5, bool(r["twitter_card"]))
    add("jsonld_present", 15, len(r["jsonld_types"]) > 0)
    add("jsonld_is_useful", 5, any(t in {"Product", "Article", "BlogPosting", "FAQPage", "HowTo", "Organization", "BreadcrumbList"} for t in r["jsonld_types"]))
    add("h1_present", 5, r["h1_count"] >= 1)
    add("h1_unique", 5, r["h1_count"] == 1)
    add("alt_coverage", 5, (r["alt_ratio"] is None) or (r["alt_ratio"] >= 0.7))
    add("readability_good", 10, r["readability_flesch"] >= 60)

    total = min(100, score)
    return {"total": total, "signals": signals}

def audit_url(url: str, timeout: int = 15) -> Dict[str, Any]:
    html = _fetch(url, timeout=timeout)
    return audit_html(html, url=url)
