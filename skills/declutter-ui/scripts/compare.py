import html
import json
import os
import sys

from PIL import Image, ImageChops

USAGE = """uso:
  python3 -I compare.py diff <pasta>                compara <pasta>/antes e <pasta>/depois pixel a pixel
  python3 -I compare.py build <pasta> <pares.json>  gera <pasta>/pagina com index.html e as imagens"""

KINDS = (("antes", "Antes"), ("depois", "Depois"))


def diff(root):
    before_dir = os.path.join(root, "antes")
    after_dir = os.path.join(root, "depois")
    names = sorted(
        name
        for name in set(os.listdir(before_dir)) | set(os.listdir(after_dir))
        if name.lower().endswith(".png")
    )
    for name in names:
        before = os.path.join(before_dir, name)
        after = os.path.join(after_dir, name)
        if not os.path.exists(before) or not os.path.exists(after):
            print("SÓ-UM-LADO", name)
            continue
        a = Image.open(before).convert("RGB")
        b = Image.open(after).convert("RGB")
        if a.size != b.size:
            print("TAMANHO", name, f"{a.size[0]}x{a.size[1]} -> {b.size[0]}x{b.size[1]}")
            continue
        box = ImageChops.difference(a, b).getbbox()
        print("MUDOU" if box else "IGUAL", name, box or "")


WEBP_MAX_SIDE = 16383


def export(source, target_base):
    image = Image.open(source).convert("RGB")
    if max(image.size) <= WEBP_MAX_SIDE:
        image.save(target_base + ".webp", "WEBP", quality=88, method=6)
        return os.path.basename(target_base) + ".webp", image.size
    image.save(target_base + ".png", "PNG", optimize=True)
    return os.path.basename(target_base) + ".png", image.size


def figure(kind, label, name, exported):
    filename, (width, height) = exported[(kind, name)]
    src = f"{kind}/{filename}"
    return (
        f'<figure class="shot"><figcaption><span class="tag tag-{kind}">{label}</span></figcaption>'
        f'<a href="{src}" target="_blank" rel="noopener"><img src="{src}" width="{width}" height="{height}" '
        f'loading="lazy" alt="{label}: {html.escape(name)}"></a></figure>'
    )


def build(root, spec_file):
    with open(spec_file) as handle:
        spec = json.load(handle)
    items = spec["items"]
    labels = spec.get("groups", {})
    out = os.path.join(root, "pagina")

    exported = {}
    for kind, _ in KINDS:
        os.makedirs(os.path.join(out, kind), exist_ok=True)
        for item in items:
            name = item["name"]
            exported[(kind, name)] = export(
                os.path.join(root, kind, name + ".png"), os.path.join(out, kind, name)
            )

    groups = []
    for item in items:
        group = item.get("group", "")
        if group not in groups:
            groups.append(group)

    sections = []
    nav = []
    for group in groups:
        rows = [item for item in items if item.get("group", "") == group]
        cards = "".join(
            f'<article class="pair" id="{html.escape(item["name"])}"><header><h3>{html.escape(item["title"])}</h3>'
            f'<p>{html.escape(item["note"])}</p></header><div class="pair-grid">'
            + "".join(figure(kind, label, item["name"], exported) for kind, label in KINDS)
            + "</div></article>"
            for item in rows
        )
        if group:
            label = html.escape(labels.get(group, group))
            anchor = html.escape(group)
            sections.append(
                f'<section class="group" id="{anchor}"><h2>{label} <span class="count">{len(rows)}</span></h2>{cards}</section>'
            )
            nav.append(f'<a href="#{anchor}">{label} <span>{len(rows)}</span></a>')
        else:
            sections.append(f'<section class="group">{cards}</section>')

    missing = f'<p class="note">{html.escape(spec["missing"])}</p>' if spec.get("missing") else ""
    nav_html = f'<nav aria-label="Seções">{"".join(nav)}</nav>' if len(nav) > 1 else ""

    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "compare.html")) as handle:
        template = handle.read()

    page = (
        template.replace("{{TITLE}}", html.escape(spec["title"]))
        .replace("{{INTRO}}", html.escape(spec.get("intro", "")))
        .replace("{{NAV}}", nav_html)
        .replace("{{MISSING}}", missing)
        .replace("{{SECTIONS}}", "".join(sections))
    )

    with open(os.path.join(out, "index.html"), "w") as handle:
        handle.write(page)

    print(f"{len(items)} pares em {out}")


if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "diff":
        diff(sys.argv[2])
    elif len(sys.argv) >= 4 and sys.argv[1] == "build":
        build(sys.argv[2], sys.argv[3])
    else:
        print(USAGE)
        sys.exit(1)
