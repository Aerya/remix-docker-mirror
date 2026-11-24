"""Preserve the public historical image address without executing image content."""
import json
import os
import re
import subprocess
import tempfile

SOURCE = "ghcr.io/remix-media/ether-remix"
TARGET = "ghcr.io/aerya/ether-remix"

def run(*args, **kwargs):
    return subprocess.run(args, check=True, text=True, capture_output=True, **kwargs).stdout

def mirror():
    # Never fall back to an older image when the canonical source is unavailable.
    digest = run("skopeo", "inspect", "--override-arch", "amd64", "--format", "{{.Digest}}", "docker://" + SOURCE + ":latest").strip()
    if not re.fullmatch(r"sha256:[0-9a-f]{64}", digest):
        raise RuntimeError("Digest source invalide")
    pinned = SOURCE + "@" + digest
    raw = run("skopeo", "inspect", "--raw", "docker://" + pinned)
    manifest = json.loads(raw)
    architectures = {m.get("platform", {}).get("architecture") for m in manifest.get("manifests", [])}
    if not {"amd64", "arm64"}.issubset(architectures):
        raise RuntimeError("La source doit contenir amd64 et arm64")
    # Digest pins every read/copy to the same release even if latest changes.
    info = json.loads(run("skopeo", "inspect", "--override-arch", "amd64", "docker://" + pinned))
    version = info.get("Labels", {}).get("org.opencontainers.image.version", "")
    if not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+-remix\.[0-9]+\.[0-9]+", version):
        raise RuntimeError("Version Remix absente ou invalide")
    with tempfile.TemporaryDirectory() as directory:
        auth = directory + "/auth.json"
        run("skopeo", "login", "--authfile", auth, "--username", os.environ["GHCR_USER"],
            "--password-stdin", "ghcr.io", input=os.environ["GHCR_TOKEN"])
        for tag in (version, "latest"):
            target = TARGET + ":" + tag
            try:
                current = run("skopeo", "inspect", "--raw", "--authfile", auth, "docker://" + target)
            except subprocess.CalledProcessError:
                current = ""
            if current == raw:
                print(target + " : déjà synchronisé")
                continue
            run("skopeo", "copy", "--all", "--preserve-digests", "--authfile", auth,
                "docker://" + pinned, "docker://" + target)
            checked = run("skopeo", "inspect", "--raw", "--authfile", auth, "docker://" + target)
            if checked != raw:
                raise RuntimeError("Le manifeste copié diffère de la source")
            print(target + " : " + digest)

if __name__ == "__main__":
    mirror()
