# encoding=utf8
import os
import re
import argparse

import tornado.ioloop
import tornado.web
import tornado.template


def convert_filename_to_unicode_char(filename: str):
    code_point = int(re.findall(r'\w+', filename)[0], 16)
    return chr(code_point)


svg_kanji_root = '../kanjivg/kanji'
svg_kanji_filenames = os.listdir(svg_kanji_root)

embed_svg_images = [f'<img class="lazy" title="{kanji_filename}" data-src="kanji/{kanji_filename}"/>' for kanji_filename in svg_kanji_filenames]

body = ''.join(embed_svg_images)
loader = tornado.template.Loader('.')
index = loader.load('index.tornado.template.html').generate(body=body)


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write(index)


def make_app():
    return tornado.web.Application([
        (r'/kanji/(.*)', tornado.web.StaticFileHandler, {'path': svg_kanji_root}),
        (r'/', MainHandler),
    ])


if __name__ == '__main__':
    app = make_app()
    app.listen(8080)
    tornado.ioloop.IOLoop.current().start()
