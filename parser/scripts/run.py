import argparse
import os
import logging

from parser.src.crawler import crawl, save_json 

def main():
    ap = argparse.ArgumentParser(description="Domain web content parser → JSON")
    ap.add_argument("--start-url", required=True)
    ap.add_argument("--max-pages", type=int, default=0)
    ap.add_argument("--out", default="parser/data/clean/output.json")
    ap.add_argument("--rate", type=float, default=1.0)
    args = ap.parse_args()

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    os.makedirs("parser/logs", exist_ok=True)

    logging.basicConfig(
        filename="parser/logs/app.log",
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s"
    )

    items = crawl(args.start_url, max_pages=args.max_pages, rate=args.rate)
    save_json(items, args.out)
    print(f"✅ Done. {len(items)} pages saved → {args.out}")

if __name__ == "__main__":
    main()
