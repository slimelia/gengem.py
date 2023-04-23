#!/usr/bin/env python3

import re
from configparser import ConfigParser
from pathlib import Path
from feedgen.feed import FeedGenerator

if __name__ == "__main__":
    TIMESTAMP_STRING = 'T12:00:00Z'
    config = ConfigParser()
    config.read('gengemConfig.cfg')
    rootURL = config.get('paths','rootURL')
    if not rootURL:
        raise ValueError('Expected rootURL to be set in gengemConfig.cfg')
    if rootURL[-1] == '/':
        rootURL = rootURL[:len(rootURL)-1]
    public_gemini = config.get('paths','public_gemini')
    if not public_gemini:
        raise ValueError('Expected public_gemini to be set in gengemConfig.cfg')
    if not Path(f'{public_gemini}/posts').is_dir():
        raise OSError('Expected "posts" subdirectory to exist in public_gemini directory.')
    gemlogPath = config.get('paths','gemlogFolder')
    if not gemlogPath:
        raise ValueError('Expected gemlogFolder to be set in gengemConfig.cfg')
    title = config.get('gemlog','title',fallback='My Gemlog')
    subtitle = config.get('gemlog','subtitle')
    bio = config.get('gemlog','bio')
    showTitle = config.getboolean('options','showTitleAlways',fallback=False)
    
    postPaths = Path(gemlogPath).glob('*.txt')
    posts = {}
    for post in postPaths:
        with open(post,'r',encoding='utf-8') as postFile:
            properties = postFile.readline()
            body = postFile.read()
        if re.search('(?<=\+title\s).*?(?=\s\+|$)',properties) and re.search('(?<=\+date\s).*?(?=\s\+|$)',properties):
            posts[('posts/'+str(post)[len(gemlogPath)+1:str(post).rfind('.txt')]+'.gmi').replace(' ','-')]={
                'title':re.search('(?<=\+title\s).*?(?=\s\+|$)',properties).group(),
                'date':re.search('(?<=\+date\s).*?(?=\s\+|$)',properties).group(),
                'body':body
            }
        else:
            raise ValueError(f'The .txt file {post} is missing +title and/or +date tags in the first line.')
    posts = dict(sorted(posts.items(),key=lambda post:post[1]['date'],reverse=True))
    
    feedGen = FeedGenerator()
    feedGen.title(title)
    feedGen.link(href=rootURL,rel='alternate')
    feedGen.updated(f'{posts[next(iter(posts))]["date"]}{TIMESTAMP_STRING}') #Set date to date of newest gemlog post
    feedGen.id(rootURL)
    
    gemLinks=[]
    for filename,post in posts.items():
        with open(f'{public_gemini}/{filename}','w',encoding='utf-8') as postGmi:
            if showTitle:
                postGmi.write(f'#{title}\n\n##{post["title"]}\n{post["body"]}')
            else:
                postGmi.write(f'#{post["title"]}\n{post["body"]}')
        gemLinks.append(f'=> {filename} {post["date"]} - {post["title"]}')
        feedEntry = feedGen.add_entry()
        feedEntry.title(post['title'])
        feedEntry.link(href=f'{rootURL}/posts/{filename}',rel='alternate')
        feedEntry.updated(f'{post["date"]}{TIMESTAMP_STRING}')
        feedEntry.id(f'{rootURL}/posts/{filename}')
        
    feedGen.atom_file(f'{public_gemini}/atom.xml')
    
    with open(f'{public_gemini}/gemlog.gmi','w',encoding='utf-8') as gemlogFile:
        gemlogFile.write(f'#{title}\n')
        if subtitle:
            gemlogFile.write(f'##{subtitle}\n')
        if bio:
            gemlogFile.write(f'{bio}\n')
        gemlogFile.write('\n\n')
        gemlogFile.write('\n'.join(gemLinks))
        gemlogFile.write('\n\n')
        gemlogFile.write('=> atom.xml Subscribe to feed (Atom)')
        
