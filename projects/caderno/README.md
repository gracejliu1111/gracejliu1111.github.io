# Caderno de Português

A study workspace for Brazilian Portuguese, organised around the book you're actually working
through: each chapter holds its own transcribed pages, its own vocabulary, and its own quizzes.

One file. No build step, no dependencies, no server. `index.html` is the whole app.

## The five pages

| Page | What's on it |
|---|---|
| **Livro** | Every chapter as a card, with a bar showing how much of its vocabulary is solid. Open one and you get its notes, its words, and a button to quiz just that chapter. |
| **Praticar** | Four quiz modes over any slice of your words — flashcards, multiple choice, type-the-answer (accent-aware, with an accent keypad), and listen-and-identify using the native-speaker clips. |
| **Vocabulário** | Every word across every chapter, in book order by default (also newest-first or A–Z). Search, filter by chapter, by what's due, by what keeps tripping you up, or by what still needs audio. |
| **Progresso** | Streak, minutes studied, how far through the book you are, a class log recording the date, chapter, pages and topic of every session, and the words that keep slipping. |
| **Ajustes** | Name your book, back up to JSON, load starter phrases. |

## Review schedule

Leitner boxes. A card you get right moves up a box; a card you miss drops to box 0 and comes back
later in the same session. Intervals in days: 0, 1, 3, 7, 16, 40. A word only counts as a *lapse*
once you've gotten it right before — that's what feeds "Words that keep slipping".

## Deploy to GitHub Pages

```bash
git init
git add index.html README.md
git commit -m "Caderno de Português"
git branch -M main
git remote add origin git@github.com:<your-username>/caderno.git
git push -u origin main
```

Then in the repo: **Settings → Pages → Source: Deploy from a branch → main / (root)**.
It goes live at `https://<your-username>.github.io/caderno/` within a minute or two.

To use a subdomain of a domain you already own, add a `CNAME` file containing
`portugues.yourdomain.com`, then create a CNAME record at your registrar pointing that
subdomain to `<your-username>.github.io`.

## Where your data lives on GitHub Pages

GitHub Pages serves static files and nothing else, so the app stores everything in the
browser you're using: `localStorage` for words, notes and sessions, IndexedDB for audio clips.

That means:

- **It stays on one browser.** Studying on your laptop and then opening the same URL on your
  phone gives you two separate, empty notebooks.
- **Clearing site data wipes it.** So does "Empty cache and hard reload" in some browsers.
- **Nobody else can see it** even though the page is public — the page ships no data, only the
  app. Your words never leave your machine.

So: **use Ajustes → Export JSON regularly** and commit the file to this repo. That's your backup,
and re-importing it merges rather than overwrites.

## Public repo, private data

The repository is public if you leave it public, but it contains only the app. Your study data is
never in it unless you commit an export. If you'd rather the URL itself be private, a private
repo with Pages enabled requires a paid GitHub plan.

## Importing content

Ajustes → Import JSON accepts:

```json
{
  "book": { "title": "Ponto de Encontro", "author": "Klobucka et al." },
  "chapters": [
    { "num": "4", "title": "Pretérito perfeito", "pages": "78–96" }
  ],
  "vocab": [
    { "pt": "a saudade", "en": "longing for something absent",
      "ex": "Que saudade de você!", "chapter": "Pretérito perfeito",
      "tags": ["noun", "feelings"] }
  ],
  "notes": [
    { "title": "Regular -ar endings", "source": "pp. 82–85",
      "chapter": "Pretérito perfeito", "body": "…", "date": "2026-08-28" }
  ],
  "sessions": [
    { "date": "2026-08-28", "minutes": 60, "kind": "Class",
      "chapter": "Pretérito perfeito", "pages": "82–85",
      "topic": "Pretérito perfeito — regular -ar verbs" }
  ]
}
```

The `chapter` field matches on title — an unknown one is created, a known one is reused. Nothing
imports twice: a word is skipped when its Portuguese already exists, a note when its title already
exists in that chapter, a session when its date, length and topic all match. The banner tells you
how many were skipped, so re-importing a file is always safe.

To genuinely *replace* a note with a corrected version, delete the old one first — the import will
never overwrite something you may have edited yourself.

## Ordering

Words appear in the order they were imported, which for a book import means the order they appear
in the book. Notes are ordered by the first page number in their `source` field, so `p. 9` sorts
before `pp. 11–12`; a note with no page reference sorts to the end.

## Keyboard shortcuts (Praticar)

| Key | Action |
|---|---|
| `Space` | Show answer |
| `1` or `J` | Again |
| `2` or `K` | Got it |
| `Enter` | Check / next, in the typed and multiple-choice modes |
