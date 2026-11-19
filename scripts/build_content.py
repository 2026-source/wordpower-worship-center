import json
import re
from pathlib import Path

import yaml
import markdown


# ==================================================
# WORDPOWER WORSHIP CENTER
# Générateur des messages et événements publiés
# ==================================================

ROOT = Path(__file__).resolve().parent.parent

CONTENT_DIR = ROOT / "content"
OUTPUT_FILE = ROOT / "content-data.js"


def slugify(text):
    """Créer un identifiant propre à partir d'un titre."""

    text = str(text).lower().strip()

    replacements = {
        "à": "a", "â": "a", "ä": "a",
        "é": "e", "è": "e", "ê": "e", "ë": "e",
        "î": "i", "ï": "i",
        "ô": "o", "ö": "o",
        "ù": "u", "û": "u", "ü": "u",
        "ç": "c",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    text = re.sub(r"[^a-z0-9]+", "-", text)

    return text.strip("-")


def read_markdown(file_path):
    """Lire les métadonnées YAML et le contenu Markdown."""

    text = file_path.read_text(encoding="utf-8")

    if not text.startswith("---"):
        raise ValueError(
            f"Format YAML-frontmatter manquant : {file_path}"
        )

    parts = text.split("---", 2)

    if len(parts) < 3:
        raise ValueError(
            f"Frontmatter incomplet : {file_path}"
        )

    metadata = yaml.safe_load(parts[1]) or {}
    body = parts[2].strip()

    return metadata, body


def load_collection(folder_name):
    """Charger uniquement les contenus publiés."""

    folder = CONTENT_DIR / folder_name
    results = []

    if not folder.exists():
        return results

    for file_path in folder.glob("*.md"):

        metadata, body = read_markdown(file_path)

        # Ignorer les contenus non publiés.
        if metadata.get("published") is not True:
            continue

        title = metadata.get("title", "Sans titre")
        slug = slugify(title)

        # Convertir le contenu Markdown en HTML.
        body_html = markdown.markdown(
            body,
            extensions=["extra", "nl2br"]
        )

        item = dict(metadata)

        item["title"] = title
        item["slug"] = slug
        item["body_html"] = body_html

        # Lien unique du message ou de l'événement.
        if folder_name == "messages":
            item["url"] = "#message-" + slug
        else:
            item["url"] = "#evenement-" + slug

        results.append(item)

    # Trier du plus récent au plus ancien.
    results.sort(
        key=lambda item: str(item.get("date", "")),
        reverse=True
    )

    return results


def main():

    messages = load_collection("messages")
    evenements = load_collection("evenements")

    data = {
        "messages": messages,
        "evenements": evenements
    }

    OUTPUT_FILE.write_text(
        "window.WORDPOWER_CONTENT = "
        + json.dumps(
            data,
            ensure_ascii=False,
            default=str
        )
        + ";\n",
        encoding="utf-8"
    )

    print("Génération WordPower terminée.")
    print(f"Messages publiés : {len(messages)}")
    print(f"Événements publiés : {len(evenements)}")


if __name__ == "__main__":
    main()