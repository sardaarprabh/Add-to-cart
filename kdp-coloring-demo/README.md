# KDP Coloring Book: Demo and Starter Kit

This is a working demo of a print-ready Amazon KDP paperback coloring book. Everything in it was generated with code.

| File | What it is |
|---|---|
| `interior.pdf` | 30-page interior, 8.5" x 11", black ink, no bleed. It has a title page, a copyright page, a color test page and 12 single-sided designs, each with a blank back. |
| `cover.pdf` | Full-wrap cover (back + spine + front) with 0.125" bleed, sized to the page count (17.318" x 11.25"). |
| `make_book.py` | The generator. Change `TITLE`, `SUBTITLE`, `AUTHOR`, `n_designs` or `seed` to get a new book. |
| `preview-*.png` | Low-res previews. |

Regenerate with: `pip install reportlab && python3 make_book.py .`

## Before uploading a real book
- Use about 40-50 designs (roughly 90-104 pages). A 12-design book is too thin to sell well.
- Spine text is only allowed when the book has more than 79 pages. Add it once the book is that long.
- Check the cover size against KDP's own cover calculator/template for your final page count and paper type.
- Use KDP's **Print Previewer** and order a **proof copy** before publishing.
- Answer KDP's AI-content question honestly for each title (see the main notes).

## Unit economics (US, 8.5x11 black ink, white paper, ~100 pages)
Printing cost is about $2.30 (flat fee for short books). Check the exact cost in KDP's pricing calculator.

| List price | Royalty rate | Royalty per sale |
|---|---|---|
| $7.99 | 50% | $4.00 - $2.30 = **~$1.70** |
| $8.99 | 50% | $4.50 - $2.30 = **~$2.20** |
| $9.99 | 60% | $5.99 - $2.30 = **~$3.69** |

Since June 2025, books priced below about $9.99 / £7.99 / €9.99 earn 50% instead of 60%.
