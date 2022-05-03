#!/usr/bin/env python3

import os
import shutil
from pathlib import Path
import re
import subprocess
import shutil

docroot = 'base_repo/docs'
wikiroot = 'wiki'

gh_name = os.environ['GITHUB_ACTOR']
gh_token = os.environ['GH_TOKEN']
gh_repo = 'https://' + gh_name + '@github.com/' + os.environ['GITHUB_REPOSITORY'] + ".git"
gh_wiki_repo = 'https://' + gh_name + ':' + gh_token + '@github.com/' + os.environ['GITHUB_REPOSITORY'] + ".wiki.git"

os.mkdir(wikiroot)

cmdd = f'git clone {gh_repo} base_repo'
print(cmdd)
cmdd = f'git clone {gh_wiki_repo} wiki_repo'
print(cmdd)

# Clone the base repo
subprocess.run(f'/usr/bin/git clone {gh_repo} base_repo', shell=True)
# Clone the wiki repo
subprocess.run(f'/usr/bin/git clone {gh_wiki_repo} wiki_repo', shell=True)

toc = []

def clean_ordering_numbers_from_path(arg):
    exploded_path = str(arg).split('/')
    new_path = []
    for segment in exploded_path:
        if re.search('^[0-9]+\-', segment):
            segment = segment.split('-', 1)[1]
        new_path.append(segment)
    fixed_path = os.path.join(*new_path)
    print(f'Fixed: {fixed_path}')
    return fixed_path


for root, dirs, files in os.walk(docroot):
    #print(os.path.relpath(root, docroot))
    print(f'root: {root}')
    #print(dirs)

    depth = str(os.path.relpath(root, docroot)).count('/')
    dir_title = clean_ordering_numbers_from_path(os.path.relpath(root, docroot).split('/')[-1].replace('_', ' '))
    dir_path = None

    if(os.path.exists(Path(root, 'index.md'))):
        print('index found')

        dir_path = clean_ordering_numbers_from_path(Path(os.path.relpath(root, docroot), 'index.md')).replace('/', '-').rsplit('.', 1)[0]


    if dir_title != '.':
        toc.append({'depth': depth, 'title': dir_title, 'path': dir_path, 'is_dir': True})

    for f in sorted(files):
        depth = str(Path(os.path.relpath(root, docroot), f)).count('/')

        src = Path(root, f)

        print("src: " + str(src))

        fixed_path = clean_ordering_numbers_from_path(Path(os.path.relpath(root, docroot), f))

        dst_filename = fixed_path.replace('/', '-')
        title = clean_ordering_numbers_from_path(f).rsplit('.')[0]

        path = dst_filename.rsplit('.', 1)[0]
        dst = Path(wikiroot, dst_filename)

        print("dst: " + str(dst))
        shutil.copy(src, dst)

        skip_files = ['Home.md', '_Footer.md', '_Sidebar.md', 'index.md']

        if str(f) in skip_files:
            continue

        with open(src) as infile:
            firstline = infile.readline()
            if len(firstline) > 0:
                if firstline[0] == '#':
                    title = firstline[1:].strip()
                    print(title)

        toc.append({'depth': depth, 'title': title, 'path': path, 'is_dir': False})

print(toc)

tocstring = ''

for item in toc:
    if item['is_dir']:
        for _ in range(item['depth']):
            tocstring += '  '
        if item['path'] != None:
            tocstring += f'* [{item["title"]}]({item["path"]})'
        else:
            tocstring += f'* **{item["title"]}**'
    else:
        for _ in range(item['depth']):
            tocstring += '  '
        tocstring += f'* [{item["title"]}]({item["path"]})'
    tocstring += '\n'

with open(Path(wikiroot, '_Sidebar.md'), 'w') as outfile:
    outfile.write(tocstring)

with open(Path(wikiroot, '_Footer.md'), 'w') as outfile:
    pass

with open(Path(wikiroot, 'Home.md'), 'w') as outfile:
    outfile.write(tocstring)

print(os.listdir('base_repo'))



print("Clean the wiki repo...")
subprocess.run(f'rm -rf wiki_repo/*', shell=True)

print("Copy the files in to the wiki repo...")
subprocess.run(f'cp wiki/* wiki_repo', shell=True)


print(os.listdir(wikiroot))
print(os.listdir('wiki_repo'))


o = subprocess.run(f'git config --global user.name "Github Actions"', shell=True, capture_output=True)
print(o.stdout)
print(o.stderr)

o = subprocess.run(f'git config --global user.email actions@github.com', shell=True, capture_output=True)
print(o.stdout)
print(o.stderr)



# Commit the wiki repo
print("Commit the repo...")
o = subprocess.run(f'git -C "./wiki_repo" add -A', shell=True, capture_output=True)
print(o.stdout)
print(o.stderr)

o = subprocess.run(f'git -C "./wiki_repo" commit -m "Github action commit"', shell=True, capture_output=True)
print(o.stdout)
print(o.stderr)

o = subprocess.run(f'git -C "./wiki_repo" push ', shell=True, capture_output=True)
print(o.stdout)
print(o.stderr)
