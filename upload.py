"""Upload PNGs to GitHub and print public raw URLs.
Usage: GH_TOKEN=... python3 upload.py OWNER REPO FOLDER_ON_REPO LOCAL_DIR"""
import os, sys, json, base64, pathlib, urllib.request

def put(owner, repo, path, data, token):
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    h = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json", "User-Agent": "thezip"}
    sha = None
    try:
        r = urllib.request.urlopen(urllib.request.Request(url, headers=h))
        sha = json.load(r)["sha"]
    except Exception:
        pass
    body = {"message": f"add {path}", "content": base64.b64encode(data).decode()}
    if sha: body["sha"] = sha
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers=h, method="PUT")
    urllib.request.urlopen(req).read()

def main(owner, repo, folder, local):
    token = os.environ["GH_TOKEN"]
    files = sorted(pathlib.Path(local).glob("*.png"))
    for f in files:
        put(owner, repo, f"{folder}/{f.name}", f.read_bytes(), token)
        print(f"https://raw.githubusercontent.com/{owner}/{repo}/main/{folder}/{f.name}")

if __name__ == "__main__":
    main(*sys.argv[1:5])
