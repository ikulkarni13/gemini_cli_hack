import os
from pathlib import Path

TEXT_EXTS = {
    ".txt", ".md", ".py", ".js", ".ts", ".tsx", ".json", ".csv",
    ".html", ".css", ".yml", ".yaml", ".toml", ".pdf"
}
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}  # NEW

def list_files(root: str, max_files: int = 80):
    p = Path(root).expanduser().resolve()
    files = []
    for dirpath, _, filenames in os.walk(p):
        for fn in filenames:
            if len(files) >= max_files:
                return files
            ext = Path(fn).suffix.lower()
            if ext in TEXT_EXTS or ext in IMAGE_EXTS:  # include images
                files.append(Path(dirpath) / fn)
    return files

def _read_text_file(path: Path, max_bytes: int = 32_000) -> str:
    try:
        with open(path, "rb") as f:
            data = f.read(max_bytes)
        return data.decode("utf-8", errors="ignore")
    except Exception:
        return ""

def _read_pdf(path: Path, max_pages: int = 1) -> str:
    try:
        from pypdf import PdfReader
        if path.stat().st_size > 10 * 1024 * 1024:
            return ""  # skip huge PDFs for speed
        reader = PdfReader(str(path))
        out = []
        for pg in reader.pages[:max_pages]:
            text = pg.extract_text() or ""
            if text:
                out.append(text)
        return "\n".join(out)
    except Exception:
        return ""

def _image_meta_snippet(path: Path) -> str:
    """Quick, local-only description: filename + (WxH + camera if available)."""
    # Works even without Pillow
    base = f"image:{path.stem}"
    try:
        from PIL import Image, ExifTags  # optional
        with Image.open(path) as im:
            w, h = im.size
            camera = None
            exif = getattr(im, "_getexif", lambda: None)()
            if exif:
                # Map EXIF tags to names
                tag_map = {ExifTags.TAGS.get(k, k): v for k, v in exif.items()}
                camera = tag_map.get("Model") or tag_map.get("Make")
            parts = [base, f"{w}x{h}"]
            if camera:
                parts.append(str(camera))
            return " • ".join(parts)
    except Exception:
        return base  # no Pillow or no EXIF

def safe_read(path: Path, max_bytes: int = 32_000) -> str:
    ext = path.suffix.lower()
    if ext == ".pdf":
        return _read_pdf(path)
    if ext in IMAGE_EXTS:
        return _image_meta_snippet(path)  # use metadata/filename as “snippet”
    return _read_text_file(path, max_bytes=max_bytes)

def build_context_snippets(paths, per_file_chars: int = 200):  # tighter for speed
    items = []
    for p in paths:
        snippet = (safe_read(p) or p.stem)[:per_file_chars]
        if not snippet.strip():
            continue
        items.append({
            "path": str(p),
            "name": p.name,
            "ext": p.suffix.lower(),
            "snippet": snippet
        })
    return items
