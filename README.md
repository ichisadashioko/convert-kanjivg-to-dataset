# Convert [kanjivg](https://github.com/KanjiVG/kanjivg) to writing dataset

After creating a machine learning model to recognize handwriting Japanese
characters from image, it seems that the model is vulnerable to similar
characters. For example: か versus が. Some of more completed characters may
never be shown in the top 10.

I set out to develop a model that recognize Japanese handwriting from the
writing strokes. In order to collect dataset for the training, I decided to
parse the `kanjivg` project's SVG files for writing strokes data.

I use `kanjivg` because I use [Jisho.org](https://jisho.org) a lot to learn
Japanese and it has some "GIF" animation to show how kanji should be written.
I dig through the [about page](https://jisho.org/about) and found `kanjivg`.

# Note about `kanjivg`

- Kanji strokes is described as SVG path on an area of size 109x109.
- There are a bunch of svg files in the [`kanji`](./kanjivg/kanji) directory
where the file name is the unicode code point.