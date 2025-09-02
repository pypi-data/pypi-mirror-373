import argparse
import json
from .audit import audit_url
from .keywords import keywords_from_url, keywords_from_text, competitor_keywords

def cmd_audit(args):
    report = audit_url(args.url)
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(f"URL: {report['url']}")
        print(f"Score: {report['score']['total']}")
        for k, v in report.items():
            if k in {"url", "score"}: continue
            print(f"- {k}: {v}")

def cmd_keywords(args):
    if args.target.startswith(("http://", "https://")):
        pairs = keywords_from_url(args.target, top_n=args.top)
    else:
        text = open(args.target, "r", encoding="utf-8", errors="ignore").read()
        pairs = keywords_from_text(text, top_n=args.top)
    if args.json:
        print(json.dumps([{"phrase": k, "score": s} for k, s in pairs], indent=2, ensure_ascii=False))
    else:
        for k, s in pairs:
            print(f"{k}\t{s:.2f}")

def cmd_competitors(args):
    data = competitor_keywords(args.urls, top_n=args.top)
    if args.json:
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        print("# Aggregate")
        for k, s in data["aggregate"]:
            print(f"{k}\t{s:.2f}")
        print("\n# Overlap (keyword appears in N URLs)")
        for k, c in data["overlap"]:
            print(f"{k}\t{c}")
        print("\n# Per URL")
        for u, pairs in data["per_url"].items():
            print(f"## {u}")
            for k, s in pairs:
                print(f"{k}\t{s:.2f}")

def main():
    p = argparse.ArgumentParser(prog="consumableai-aeo", description="AEO/GEO auditor and keyword extractor")
    sub = p.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("audit", help="Audit AEO/GEO signals from a URL")
    a.add_argument("url")
    a.add_argument("--json", action="store_true")
    a.set_defaults(func=cmd_audit)

    k = sub.add_parser("keywords", help="Extract keywords from URL or file")
    k.add_argument("target")
    k.add_argument("--top", type=int, default=25)
    k.add_argument("--json", action="store_true")
    k.set_defaults(func=cmd_keywords)

    c = sub.add_parser("competitors", help="Compare competitor keywords across URLs")
    c.add_argument("urls", nargs="+")
    c.add_argument("--top", type=int, default=20)
    c.add_argument("--json", action="store_true")
    c.set_defaults(func=cmd_competitors)

    args = p.parse_args()
    return args.func(args)
