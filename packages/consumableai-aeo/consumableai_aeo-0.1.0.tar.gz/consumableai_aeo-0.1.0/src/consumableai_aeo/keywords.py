import re
from typing import List, Dict, Iterable, Tuple
import requests
from bs4 import BeautifulSoup

USER_AGENT = "consumableai-aeo/0.1 (+https://www.consumableai.com)"

STOPWORDS = set("""
a about above after again against all am an and any are aren't as at be because been before being below
between both but by can't cannot could couldn't did didn't do does doesn't doing don't down during each
few for from further had hadn't has hasn't have haven't having he he'd he'll he's her here here's hers
herself him himself his how how's i i'd i'll i'm i've if in into is isn't it it's its itself let's me
more most mustn't my myself no nor not of off on once only or other ought our ours ourselves out over
own same shan't she she'd she'll she's should shouldn't so some such than that that's the their theirs
them themselves then there there's these they they'd they'll they're they've this those through to too
under until up very was wasn't we we'd we'll we're we've were weren't what what's when when's where
where's which while who who's whom why why's with won't would wouldn't you you'd you'll you're you've your yours yourself yourselves
""".split())

def _fetch(url: str, timeout: int = 15) -> str:
    resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=timeout)
    resp.raise_for_status()
    return resp.text

def _visible_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    return " ".join(soup.stripped_strings)

def _candidate_phrases(text: str) -> List[str]:
    text = re.sub(r"[^a-zA-Z0-9\s-]", " ", text)
    words = [w.lower() for w in text.split()]
    phrases = []
    buf = []
    for w in words:
        if w in STOPWORDS:
            if buf:
                phrases.append(" ".join(buf))
                buf = []
        else:
            buf.append(w)
    if buf:
        phrases.append(" ".join(buf))
    phrases = [p.strip("- ").strip() for p in phrases if len(p) >= 3]
    return phrases

def _rake_score(phrases: List[str]) -> Dict[str, float]:
    freq = {}
    degree = {}
    for p in phrases:
        terms = p.split()
        degree_p = max(0, len(terms) - 1)
        for t in terms:
            freq[t] = freq.get(t, 0) + 1
            degree[t] = degree.get(t, 0) + degree_p
    score = {}
    for p in phrases:
        terms = p.split()
        s = sum((degree[t] + freq[t]) / max(1, freq[t]) for t in terms)
        score[p] = score.get(p, 0) + s
    return score

def keywords_from_text(text: str, top_n: int = 25) -> List[Tuple[str, float]]:
    phrases = _candidate_phrases(text)
    scores = _rake_score(phrases)
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return ranked[:top_n]

def keywords_from_url(url: str, top_n: int = 25, timeout: int = 15) -> List[Tuple[str, float]]:
    html = _fetch(url, timeout=timeout)
    text = _visible_text(html)
    return keywords_from_text(text, top_n=top_n)

def competitor_keywords(urls: Iterable[str], top_n: int = 20, timeout: int = 15):
    per_url = {}
    global_scores = {}
    for u in urls:
        kws = keywords_from_url(u, top_n=top_n, timeout=timeout)
        per_url[u] = kws
        for k, s in kws:
            global_scores[k] = global_scores.get(k, 0) + s
    aggregate = sorted(global_scores.items(), key=lambda x: x[1], reverse=True)[:top_n]
    counts = {}
    for u, kws in per_url.items():
        for k, _ in kws:
            counts[k] = counts.get(k, 0) + 1
    overlap = [(k, c) for k, c in counts.items() if c > 1]
    overlap.sort(key=lambda x: (-x[1], x[0]))
    return {"aggregate": aggregate, "overlap": overlap, "per_url": per_url}
