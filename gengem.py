#!/usr/bin/env python3

"""Simple Python script to generate a Gemini gemlog
and accompanying Atom feed.
"""

import re
import sys
from configparser import ConfigParser
from pathlib import Path
from feedgen.feed import FeedGenerator  # type: ignore
from feedgen.entry import FeedEntry  # type: ignore

if __name__ == "__main__":
    if sys.version_info < (3, 7):
        raise SystemError('Python version must be 3.7 or higher')

    TIMESTAMP_STRING: str = 'T12:00:00Z'
    config: ConfigParser = ConfigParser()
    config.read('gengemConfig.cfg')
    rootURL: str = config.get('paths', 'rootURL')
    if not rootURL:
        raise ValueError('Expected rootURL to be set in gengemConfig.cfg')
    if rootURL[-1] == '/':
        rootURL = rootURL[:len(rootURL)-1]
    public_gemini: str = config.get('paths', 'public_gemini')
    if not public_gemini:
        raise ValueError('Expected public_gemini to be set in'
                         ' gengemConfig.cfg')
    if not Path(f'{public_gemini}/posts').is_dir():
        raise OSError('Expected "posts" subdirectory to exist in'
                      ' public_gemini directory.')
    gemlogPath: str = config.get('paths', 'gemlogFolder')
    if not gemlogPath:
        raise ValueError('Expected gemlogFolder to be set in gengemConfig.cfg')
    title: str = config.get('gemlog', 'title', fallback='My Gemlog')
    subtitle = config.get('gemlog', 'subtitle')
    bio: str = config.get('gemlog', 'bio')
    showTitle: bool = config.getboolean('options',
                                        'showTitleAlways', fallback=False)

    postPaths = Path(gemlogPath).glob('*.txt')
    posts: dict[str, dict] = {}
    for post in postPaths:
        with open(post, 'r', encoding='utf-8') as postFile:
            properties: str = postFile.readline()
            body: str = postFile.read()
        if ((postTitle := re.search(r'(?<=\+title\s).*?(?=\s\+|$)',
             properties)) is not None
            and (postDate := re.search(r'(?<=\+date\s).*?(?=\s\+|$)',
                 properties)) is not None):
            posts[('posts/' +
                   str(post)[len(gemlogPath) + 1:str(post).rfind('.txt')] +
                   '.gmi').replace(' ', '-')] = {
                        'title': postTitle.group(),
                        'date': postDate.group(),
                        'body': body
                }
        else:
            raise ValueError(f'The .txt file {post} is missing +title and/or'
                             ' +date tags in the first line.')

    posts = dict(sorted(((filename,
                          postItem) for filename, postItem in posts.items()),
                        key=lambda post: post[1]['date'], reverse=True))

    feedGen: FeedGenerator = FeedGenerator()
    feedGen.title(title)
    feedGen.link(href=rootURL, rel='alternate')
    # Set date to date of newest gemlog post
    feedGen.updated(f'{posts[next(iter(posts))]["date"]}{TIMESTAMP_STRING}')
    feedGen.id(rootURL)

    gemLinks: list[str] = []
    for filename, postItem in posts.items():
        with open(f'{public_gemini}/{filename}', 'w',
                  encoding='utf-8') as postGmi:
            if showTitle:
                postGmi.write(f'#{title}\n\n'
                              f'##{postItem["title"]}\n{postItem["body"]}')
            else:
                postGmi.write(f'#{postItem["title"]}\n{postItem["body"]}')
        gemLinks.append(f'=> {filename} {postItem["date"]} '
                        f'- {postItem["title"]}')
        atomFeedEntry: FeedEntry = feedGen.add_entry()
        atomFeedEntry.title(postItem['title'])
        atomFeedEntry.link(href=f'{rootURL}/{filename}', rel='alternate')
        atomFeedEntry.updated(f'{postItem["date"]}{TIMESTAMP_STRING}')
        atomFeedEntry.id(f'{rootURL}/posts/{filename}')

    feedGen.atom_file(f'{public_gemini}/atom.xml')

    with open(f'{public_gemini}/gemlog.gmi', 'w',
              encoding='utf-8') as gemlogFile:
        gemlogFile.write(f'#{title}\n')
        if subtitle:
            gemlogFile.write(f'##{subtitle}\n')
        if bio:
            gemlogFile.write(f'{bio}\n')
        gemlogFile.write('\n\n')
        gemlogFile.write('\n'.join(gemLinks))
        gemlogFile.write('\n\n')
        gemlogFile.write('=> atom.xml Subscribe to feed (Atom)')
