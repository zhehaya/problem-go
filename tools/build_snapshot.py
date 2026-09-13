# -*- coding: utf-8 -*-
"""生成离线题库快照 data/problems.js（5+ App 里开机即可用，无需先下载 10MB 的 API 数据）。

用法（在项目根目录执行）：
    python tools/build_snapshot.py
"""
import json
import os
import time
import urllib.request

API = "https://codeforces.com/api/problemset.problems"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "problems.js")


def main():
    req = urllib.request.Request(API, headers={
        "User-Agent": UA,
        "Accept": "application/json",
        "Accept-Language": "en-US,en;q=0.9",
    })
    with urllib.request.urlopen(req, timeout=90) as r:
        data = json.loads(r.read().decode("utf-8"))
    if data.get("status") != "OK" or "result" not in data:
        raise SystemExit("API 返回异常：" + str(data)[:200])

    solved = {}
    for s in data["result"].get("problemStatistics", []):
        solved[(s.get("contestId"), s.get("index"))] = s.get("solvedCount", 0)

    packed = []
    for p in data["result"].get("problems", []):
        cid, idx = p.get("contestId"), p.get("index")
        rating = p.get("rating")
        if not cid or not idx or not isinstance(rating, int):
            continue                      # 未评级题目跳过
        if p.get("type") and p["type"] != "PROGRAMMING":
            continue
        packed.append([cid, idx, p["name"], rating,
                       "\u0001".join(p.get("tags") or []),
                       solved.get((cid, idx), 0)])
    packed.sort(key=lambda x: (x[3], x[0], x[1]))

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write("/* 离线题库快照（自动生成，请勿手改）\n"
                "   生成时间：%s\n"
                "   题目数量：%d\n"
                "   重新生成：python tools/build_snapshot.py */\n"
                "window.CF_PROBLEMS_SNAPSHOT = " % (time.strftime("%Y-%m-%d %H:%M"), len(packed)))
        json.dump({"ts": int(time.time() * 1000), "list": packed},
                  f, ensure_ascii=False, separators=(",", ":"))
        f.write(";\n")

    print("OK  %d problems  ->  %s  (%.0f KB)"
          % (len(packed), OUT, os.path.getsize(OUT) / 1024.0))


if __name__ == "__main__":
    main()
