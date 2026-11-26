#!/usr/bin/env python3
"""MICROCORE collection and audit pipeline.

Subcommands
-----------
manifest                 print the acquisition manifest
fetch --id MC-001 [...]  stream-download with resume, hash, and a JSONL audit log
hash --path FILE         sha256 + size for any local artefact
dedup --input records.jsonl --text-field text [--threshold 0.8]
leakage --input records.jsonl --text-field text --group-field cve_id
scan --input records.jsonl --text-field text

Nothing here executes downloaded content. Binaries are hashed and quarantined,
never run. Every run appends to out/audit_log.jsonl with a UTC timestamp so the
date of each check is preserved.
"""
import argparse, bz2, gzip, hashlib, json, os, re, sys, time, urllib.request, urllib.error
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "out")
RAW = os.path.join(ROOT, "raw", "dl")
MANIFEST = os.path.join(ROOT, "pipeline", "manifest.json")
UA = "MICROCORE-audit/1.0 (dataset provenance verification; contact: research)"


def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def log(entry):
    os.makedirs(OUT, exist_ok=True)
    entry["ts_utc"] = now()
    with open(os.path.join(OUT, "audit_log.jsonl"), "a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")


def sha256_file(path, block=1 << 20):
    h = hashlib.sha256()
    n = 0
    with open(path, "rb") as fh:
        while True:
            b = fh.read(block)
            if not b:
                break
            h.update(b)
            n += len(b)
    return h.hexdigest(), n


def cmd_manifest(args):
    m = json.load(open(MANIFEST, encoding="utf-8"))
    for s in m["sources"]:
        print(f"{s['id']:8s} {s['access']:24s} {str(s.get('expected_bytes','?')):>13s}  {s['name'][:58]}")


def cmd_fetch(args):
    m = {s["id"]: s for s in json.load(open(MANIFEST, encoding="utf-8"))["sources"]}
    for sid in args.id:
        s = m[sid]
        if s["access"] != "VERIFIED_ACCESSIBLE":
            print(f"{sid}: skipped, manifest access is {s['access']} - refusing to fetch")
            log({"id": sid, "action": "fetch", "result": "skipped_access_class", "access": s["access"]})
            continue
        dest = os.path.join(RAW, s["filename"])
        os.makedirs(RAW, exist_ok=True)
        have = os.path.getsize(dest) if os.path.exists(dest) else 0
        req = urllib.request.Request(s["url"], headers={"User-Agent": UA})
        if have:
            req.add_header("Range", f"bytes={have}-")
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                code = r.status
                total = r.headers.get("Content-Length")
                mode = "ab" if have and code == 206 else "wb"
                if mode == "wb":
                    have = 0
                with open(dest, mode) as fh:
                    while True:
                        b = r.read(1 << 20)
                        if not b:
                            break
                        fh.write(b)
            digest, size = sha256_file(dest)
            expect = s.get("expected_sha256")
            verdict = "sha256_match" if expect and digest.lower() == expect.lower() else (
                "sha256_mismatch" if expect else "sha256_recorded_no_reference")
            print(f"{sid}: HTTP {code} -> {size} B  sha256={digest}  {verdict}")
            log({"id": sid, "action": "fetch", "http": code, "bytes": int(total) if total else None,
                 "local_bytes": size, "sha256": digest, "verdict": verdict, "url": s["url"]})
        except urllib.error.HTTPError as e:
            print(f"{sid}: HTTP {e.code} - recorded, not retried")
            log({"id": sid, "action": "fetch", "http": e.code, "result": "http_error", "url": s["url"]})
        except Exception as e:  # network, TLS, timeout
            print(f"{sid}: transient failure {type(e).__name__}: {e}")
            log({"id": sid, "action": "fetch", "result": "temporary_failure", "error": str(e), "url": s["url"]})


def cmd_hash(args):
    digest, size = sha256_file(args.path)
    print(json.dumps({"path": args.path, "bytes": size, "sha256": digest}, indent=1))
    log({"action": "hash", "path": args.path, "bytes": size, "sha256": digest})


# ---------- near-duplicate detection (MinHash over word 5-grams) ----------

def shingles(text, k=5, cap=512):
    toks = re.findall(r"[a-z0-9_]+", text.lower())
    if len(toks) < k:
        return {" ".join(toks)} if toks else set()
    grams = {" ".join(toks[i:i + k]) for i in range(len(toks) - k + 1)}
    if len(grams) > cap:  # deterministic subsample keeps signatures comparable
        grams = set(sorted(grams)[:cap])
    return grams


def minhash(grams, n=64):
    if not grams:
        return tuple([0] * n)
    sig = []
    for i in range(n):
        m = min(int.from_bytes(hashlib.blake2b((f"{i}:" + g).encode(), digest_size=8).digest(), "big") for g in grams)
        sig.append(m)
    return tuple(sig)


def iter_records(path, text_field):
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            yield obj, str(obj.get(text_field, ""))


def cmd_dedup(args):
    seen_hash, seen_sig = {}, []
    exact, near, kept = 0, 0, 0
    with open(args.report, "w", encoding="utf-8") as rep:
        for obj, text in iter_records(args.input, args.text_field):
            h = hashlib.sha256(text.strip().encode()).hexdigest()
            if h in seen_hash:
                exact += 1
                rep.write(json.dumps({"verdict": "exact_duplicate", "of": seen_hash[h], "id": obj.get("id")}) + "\n")
                continue
            seen_hash[h] = obj.get("id")
            sig = minhash(shingles(text))
            dup = None
            for other_id, other in seen_sig:
                same = sum(1 for a, b in zip(sig, other) if a == b) / len(sig)
                if same >= args.threshold:
                    dup = (other_id, round(same, 3))
                    break
            if dup:
                near += 1
                rep.write(json.dumps({"verdict": "near_duplicate", "of": dup[0], "jaccard": dup[1], "id": obj.get("id")}) + "\n")
                continue
            seen_sig.append((obj.get("id"), sig))
            kept += 1
    print(json.dumps({"input": args.input, "kept": kept, "exact_duplicates": exact,
                      "near_duplicates": near, "threshold": args.threshold}, indent=1))
    log({"action": "dedup", "input": args.input, "kept": kept, "exact": exact, "near": near})


# ---------- train/eval leakage splits ----------

def stable_bucket(key, mod=100):
    return int.from_bytes(hashlib.blake2b(str(key).encode(), digest_size=4).digest(), "big") % mod


def cmd_leakage(args):
    splits = {"train": 0, "val": 0, "test": 0}
    sig_by_split = {"train": [], "val": []}
    leaked = 0
    with open(args.output, "w", encoding="utf-8") as out:
        for obj, text in iter_records(args.input, args.text_field):
            group = str(obj.get(args.group_field) or hashlib.sha256(text.encode()).hexdigest()[:16])
            b = stable_bucket(group)
            split = "train" if b < 90 else ("val" if b < 95 else "test")
            sig = minhash(shingles(text))
            if split == "test":
                for other in sig_by_split["train"] + sig_by_split["val"]:
                    if sum(1 for a, c in zip(sig, other) if a == c) / len(sig) >= args.threshold:
                        leaked += 1
                        obj["_leak_flag"] = True
                        break
            elif split in sig_by_split:
                sig_by_split[split].append(sig)
            obj["_split"] = split
            splits[split] += 1
            out.write(json.dumps(obj, ensure_ascii=False) + "\n")
    print(json.dumps({"splits": splits, "test_flagged_as_leaked": leaked,
                      "group_field": args.group_field}, indent=1))
    log({"action": "leakage_split", "input": args.input, "splits": splits, "leaked_test": leaked})


# ---------- secret / PII scan ----------

PATTERNS = {
    "private_key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |PGP )?PRIVATE KEY-----"),
    "aws_access_key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "github_token": re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
    "slack_token": re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}"),
    "jwt": re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}"),
    "email": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
    "ipv4": re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"),
    "password_assignment": re.compile(r"(?i)\b(?:password|passwd|pwd)\s*[:=]\s*\S+"),
    "ntlm_hash": re.compile(r"\b[a-fA-F0-9]{32}:[a-fA-F0-9]{32}\b"),
}


def cmd_scan(args):
    counts = {k: 0 for k in PATTERNS}
    examples = {k: [] for k in PATTERNS}
    n = 0
    for obj, text in iter_records(args.input, args.text_field):
        n += 1
        for name, pat in PATTERNS.items():
            m = pat.search(text)
            if m:
                counts[name] += 1
                if len(examples[name]) < 3:
                    examples[name].append(m.group(0)[:80])
    print(json.dumps({"records": n, "counts": counts, "examples": examples}, indent=1))
    log({"action": "scan", "input": args.input, "records": n, "counts": counts})


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("manifest").set_defaults(fn=cmd_manifest)
    f = sub.add_parser("fetch"); f.add_argument("--id", nargs="+", required=True); f.set_defaults(fn=cmd_fetch)
    h = sub.add_parser("hash"); h.add_argument("--path", required=True); h.set_defaults(fn=cmd_hash)
    d = sub.add_parser("dedup")
    d.add_argument("--input", required=True); d.add_argument("--text-field", default="text")
    d.add_argument("--threshold", type=float, default=0.8); d.add_argument("--report", default=os.path.join(OUT, "dedup_report.jsonl"))
    d.set_defaults(fn=cmd_dedup)
    l = sub.add_parser("leakage")
    l.add_argument("--input", required=True); l.add_argument("--output", required=True)
    l.add_argument("--text-field", default="text"); l.add_argument("--group-field", default="group")
    l.add_argument("--threshold", type=float, default=0.8); l.set_defaults(fn=cmd_leakage)
    s = sub.add_parser("scan"); s.add_argument("--input", required=True)
    s.add_argument("--text-field", default="text"); s.set_defaults(fn=cmd_scan)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
