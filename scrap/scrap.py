from collections import deque
import urllib2
import HTMLParser
import sys
import re
import json
import os


DATA_FOLDER = 'data/'
HTML_DATA = 'html_data/'
JSON_DATA = 'json_data/'


# Regular expressions
COMMENT_BLOCK_RE = '<ul class="flat-list buttons">[^\r\n]*<p>.*?</p>(?:\n+<p>[^\r\n]*</p>)*';
''' Explanation
1) <ul class="flat-list buttons">[^\r\n]*<p>: detect sequences '<ul class="flat-list buttons>" blablabla ... blalba <p>
2) <p>.*?</p>: sequence from <p> to </p>, with any character in between. The ? makes sure to grab as little as possible.
3) (?:\n+<p>[^\r\n]*</p>)* : sequnces  <p> to </p>, with any character in between, except from the newline.
'''

USERNAME_RE = r'http://www.reddit.com/user/[^"]*"';
CHILDREN_RE = r'\d+\s(?:children|child)';
POINTS_RE = r'\d\s(?:points|point)';
COMMENT_LINES_RE = r'<p>.*[\r\n|</p>]';
COMMENT_ID_RE = r'id-t1_[\w\b]+';
COMMENT_PARENT_RE = r'siteTable_t1_[\w\b]+';
DATETIME_RE = r'datetime="[\d\sA-Z:\-]+';



# Dictonary keys
ID = 'id';
USER = 'username';
PARENT_ID = 'parent_id'
LIST = 'children';
COMMENT = 'text';
POINTS = 'points';


# Common html codes
HTML_CODES = [('&#39;', "'",), ('&quot;','"'),('&gt;', '>'),( '&lt;', '<'),('&amp;', '&')]


def scrapUserComments(html_block):
    ''' Scrap user comments from a comment block '''
    comment_str = re.findall(COMMENT_LINES_RE, html_block, re.DOTALL)[0]
    comment_str = comment_str.replace('<p>', '').replace('</p>', '');
    for code in HTML_CODES:
        comment_str = comment_str.replace(code[0], code[1])
    # Transform References to urls
    refs = re.findall(r'<a[^\r\n]*?</a>', comment_str);
    for r in refs:
        u_list = re.findall('href=".*?"', r)
        if len(u_list) != 1 : continue
        u = u_list[0].replace("href=", ' ').replace('"','')
        comment_str =  comment_str.replace(r, u)
    # Remove html tags
    tags = re.findall('<\/?[a-z]+>', comment_str);
    for t in tags:
        comment_str = comment_str.replace(t, '')
    return comment_str



def scrapChildrenNum(html_block):
    ''' Scrap the number of children '''
    children_str = re.findall(CHILDREN_RE, html_block)[0];
    return int(children_str.replace('children', '').replace('child',''));



def scrapUsername(html_block):
    ''' Scrap username '''
    user_list = re.findall(USERNAME_RE, html_block);
    if not len(user_list):
        return None
    user_url = user_list[0] 
    return user_url.replace('http://www.reddit.com/user/', '').replace('\"','')



def scrapPoints(html_block):
    ''' Scrap the points '''
    points_str = re.findall(POINTS_RE, html_block)[1];
    return int(points_str.replace('points', '').replace('point',''));



def scrapParentName(html_block):
    ''' Get the name of the parent, of the comment '''
    matched_list = re.findall(COMMENT_PARENT_RE, html_block);
    if not len(matched_list):
        return None
    s = matched_list[0]
    return s.replace('siteTable_t1_', '');



def scrapCommentID(html_block):
    ''' Get the name of the comment '''
    matched_list = re.findall(COMMENT_ID_RE, html_block);
    if not len(matched_list):
        return None
    s = matched_list[0]
    return s.replace('id-t1_', '');



def buildCommentTree(comment_list):
    ''' Build a comment tree, fromm the list of extracted comments ''' 

    tree = {}
    for c, block in enumerate(comment_list):
        # Extract id
        ID = scrapCommentID(block)
        if not ID: continue
        # Extract other items
        node = {}       
        try:
            node[PARENT_ID] = scrapParentName(block)
            node[USER] = scrapUsername(block)
            node[COMMENT] = scrapUserComments(block) 
            node[POINTS] = scrapPoints(block)
            node[LIST] = []
        except IndexError:
            # print 'Error extracting %d'%c 
            continue
        # Add new nodes to the dictionary
        tree[ID] = node;
        # Connect nodes with their parents 
        if node[PARENT_ID] and node[PARENT_ID] in tree:
            tree[node[PARENT_ID]][LIST].append(ID) 
    return tree



def printCommentTree(tree):
    ''' Print comment in a tree structure  '''
    root_comment = [u for u in tree if not tree[u][PARENT_ID]]
    for u in root_comment:
        recursivePrint(u, tree, 0);


def recursivePrint(u, tree, depth):
    ''' Recursively print all comments that are in the same branch of the tree '''
    space = '\t'.join('' for i in range(depth+1))
    print '%s%s: %d points, %d children'%(space, tree[u][USER], tree[u][POINTS], len(tree[u][LIST]))
    print '%s%s ... \n'%(space, tree[u][COMMENT].replace('\n', '\n%s'%space)[:50])
    for v in tree[u][LIST]:
        recursivePrint(v, tree, depth+1)



def main():
    ''' Scrap info from html pages, and save them to .json files '''
    for filename in os.listdir(HTML_DATA):
        if filename.find('html')<0: continue
        print 'Scraping file %s'%filename        
        # read data
        data = open('%s%s'%(HTML_DATA, filename)).read()
        # Scrap info from html, and save it in a file
        raw_comments = re.findall(COMMENT_BLOCK_RE, data, re.DOTALL)
        tree_dict = buildCommentTree(raw_comments)
        if not len(tree_dict): continue
        new_file = filename.replace('html', 'json')
        json.dump(tree_dict, open('%s%s'%(JSON_DATA, new_file), 'w'))


 
if __name__ == '__main__':

    main();

    sys.exit()

    ''' Test code '''
    #filename = 'html_data/my_christmas_presents_to_myself_finally_turned_up.html'
    #filename = 'html_data/xlyyr.html'
    filename = 'html_data/gxou8.html'
    
    
    data = open(filename).read()

    # Extract the comment blocks
    raw_comments = re.findall(COMMENT_BLOCK_RE, data, re.DOTALL)

    # build the comment tree
    tree_dict = buildCommentTree(raw_comments)

    # show tree structure
    printCommentTree(tree_dict) 

    new_file = filename.replace('html', 'json')
    json.dump(tree_dict, open(new_file, 'w'))
