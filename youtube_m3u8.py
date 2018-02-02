#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
"""
genplaylist

Install::

    pip install -U ffprobe m3u8_generator youtube_dl

Requires:

- ffprobe (ffmpeg)
- m3u8_generator
- youtube_dl

Use cases:

- Download a youtube playlist as mp4 videos and generate an m3u8 playlist
"""
import codecs
import json
import logging
import math
import subprocess

import m3u8_generator


log = logging.getLogger()


def get_duration(path):
    cmd = ('ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_format',
        path)
    try:
        jsonstr = subprocess.check_output(cmd)
        obj = json.loads(jsonstr)
        data = obj.get('format')
        d = data.get('duration')
        durationstr = "{}.{}".format(int(float(d) // 60), int(math.ceil(float(d) % 60)))
    except subprocess.CalledProcessError as e:
        log.exception(e)
        d = 0
        durationstr = str(d)
    return durationstr


def get_playlist_json(url, fmt):
    """
    Args:
        url (str): URL of a [youtube,] playlist
        fmt (str): format extensions (e.g. 'mp4')
    Yields:
        dict: data from youtube-dl json + 'filename' key w/ fmt ext
    """
    cmd = ('youtube-dl', '-j', '--flat-playlist', url)
    output = subprocess.check_output(cmd)
    for l in output.splitlines():
        data = json.loads(l)
        data['filename'] = u"{}-{}.{}".format(
            data.get("title"),
            data.get("url"),
            fmt)
        yield data


def get_playlist_items(url, fmt, playlistjson=None):
    playlistjson = playlistjson or (obj for obj in get_playlist_json(url, fmt))
    for obj in playlistjson:
        try:
            duration = get_duration(obj['filename'])
        except Exception as e:
            log.exception(e)
            duration = 0
        yield {'name': obj['filename'], 'duration': duration}


def genplaylist(url, fmt='mp4', output='playlist.m3u8',
                playlistjson=None):
    """mainfunc

    Arguments:
         (str): ...

    Keyword Arguments:
         (str): ...

    Returns:
        str: ...

    Yields:
        str: ...

    Raises:
        Exception: ...
    """
    items = list(get_playlist_items(url, fmt, playlistjson))
    for item in items:
        log.debug(item)
    playliststr = m3u8_generator.PlaylistGenerator(items).generate()

    log.debug('## playliststr:')
    log.debug(playliststr)

    with codecs.open(output, 'w', encoding='utf8') as f:
        f.write(playliststr)

    return playliststr



import unittest


class Test_genplaylist(unittest.TestCase):

    def setUp(self):
        pass

    def test_genplaylist(self):
        url = 'https://www.youtube.com/playlist?list=PLt_DvKGJ_QLaThKOHGxSUbA5SnyY5soCV'
        output = genplaylist(url, 'mp4', 'playlist.m3u8')
        raise Exception(output)

    def tearDown(self):
        pass


def main(argv=None):
    """
    Main function

    Keyword Arguments:
        argv (list): commandline arguments (e.g. sys.argv[1:])
    Returns:
        int:
    """
    import logging
    import optparse

    prs = optparse.OptionParser(usage="%prog : args")

    prs.add_option('-v', '--verbose',
                    dest='verbose',
                    action='store_true',)
    prs.add_option('-q', '--quiet',
                    dest='quiet',
                    action='store_true',)
    prs.add_option('-t', '--test',
                    dest='run_tests',
                    action='store_true',)


    loglevel = logging.INFO
    (opts, args) = prs.parse_args(args=argv)
    if opts.verbose:
        loglevel = logging.DEBUG
    elif opts.quiet:
        loglevel = logging.ERROR
    logging.basicConfig(level=loglevel)
    log = logging.getLogger()
    argv = list(argv) if argv else []
    log.debug('argv: %r', argv)
    log.debug('opts: %r', opts)
    log.debug('args: %r', args)

    if opts.run_tests:
        import sys
        sys.argv = [sys.argv[0]] + args
        import unittest
        return unittest.main()

    EX_OK = 0
    output = genplaylist()
    return EX_OK


if __name__ == "__main__":
    import sys
    sys.exit(main(argv=sys.argv[1:]))
