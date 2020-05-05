#!/usr/bin/env python3

import argparse
import hashlib
import logging
import os
import sys

import pypandoc
import requests

BIN = os.path.dirname(__file__)

username = os.environ.get('CONFLUENCE_USERNAME')
password = os.environ.get('CONFLUENCE_PASSWORD')

session = requests.Session()
session.auth = (username, password)


def find_page(url, space, page_title):
    querystring = f"cql=title='{page_title}' and space='{space}'"
    search_url = f"{url}/rest/api/content/search?{querystring}"
    resp = session.get(search_url)
    resp.raise_for_status()
    if len(resp.json()['results']) > 0:
        return resp.json()['results'][0]
    else:
        return None


def get_page_info(url, page_id):
    url = f"{url}/rest/api/content/{page_id}?expand=ancestors,version"
    resp = session.get(url)
    resp.raise_for_status()
    return resp.json()


def create_page(url, space, page_title, ancestor=None):
    data = {
        "type": "page",
        "title": page_title,
        "space": {"key": space.strip('"')},
        "body": {
            "storage": {"value": "<p>Empty page</p>", "representation": "storage"}
        },
    }

    if ancestor:
        data['ancestors'] = [{"id": ancestor}]

    url = f"{url}/rest/api/content/"
    resp = session.post(url, json=data)

    if not resp.ok:
        print("Confluence response: \n", resp.text)

    resp.raise_for_status()

    return resp.json()


def update_page(url, page_id, markup, comment):
    info = get_page_info(url, page_id)
    url = f"{url}/rest/api/content/{page_id}"
    updated_page_version = int(info["version"]["number"] + 1)

    data = {
        'id': str(page_id),
        'type': 'page',
        'title': info['title'],
        'version': {
            'number': updated_page_version,
            'minorEdit': True,
            'message': comment,
        },
        'body': {'storage': {'representation': 'storage', 'value': markup}},
    }
    resp = session.put(url, json=data)
    if not resp.ok:
        print("Confluence response: \n", resp.json())
    resp.raise_for_status()
    return resp.json()


def getargs():
    """ Parse args from the command-line.  """
    parser = argparse.ArgumentParser(description='Publish docs')
    parser.add_argument('--confluence-url', help='URL to publish to confluence.')
    parser.add_argument('--confluence-space', help='Space to publish to confluence.')
    parser.add_argument('--dry-run', action='store_true', help='Don\'t actually update confluence.')
    parser.add_argument(
        '--path', help='Relative path to location of the docs, inside root.'
    )
    parser.add_argument('--root', help='Absolute path to the docs repo.')
    args = parser.parse_args()

    if not args.dry_run:
        if not args.confluence_url:
            print("--confluence-url is required.")
            sys.exit(1)
        if not args.confluence_space:
            print("--confluence-space is required.")
            sys.exit(1)
        if not username:
            print("CONFLUENCE_USERNAME must be defined to publish.")
            sys.exit(1)
        if not password:
            print("CONFLUENCE_PASSWORD must be defined to publish.")
            sys.exit(1)

    if not args.root:
        print("--root is required.")
        sys.exit(1)
    args.root = os.path.abspath(args.root)

    if not args.path:
        print("--path is required.")
        sys.exit(1)
    args.path = args.path.strip('/')

    return args


def publish(args):
    root = f"{args.root}/{args.path}"

    pages_by_name = {}

    def get_or_create_page(pagename, namespace):
        if not pagename:
            return
        page = pages_by_name.get(pagename)
        if not page:
            print("Searching for %s" % pagename, file=sys.stderr)
            page = find_page(
                url=args.confluence_url,
                space=args.confluence_space,
                page_title=pagename,
            )
        if not page:
            print("Creating %s" % pagename, file=sys.stderr)
            ancestor = pages_by_name[namespace]['id'] if namespace else None
            page = create_page(
                url=args.confluence_url,
                space=args.confluence_space,
                page_title=pagename,
                ancestor=ancestor,
            )
        pages_by_name[pagename] = page
        return page

    print(f"Looking for docs in {root}", file=sys.stderr)
    for base, directories, filenames in os.walk(root):
        namespace = base[len(root) :].split('/')[-1]

        if not args.dry_run:
            get_or_create_page(namespace, None)

        for filename in filenames:
            pagename, extension = filename.rsplit('.', 1)
            if extension != 'md':
                raise ValueError(f"Only markdown is supported, not {filename}")

            full_path = f'{base}/{filename}'
            with open(full_path, 'r') as f:
                markdown = f.read()

            # Add a header prefix if we can figure out where to link people to.
            # CI_PROJECT_URL is a gitlab-ci environment variable.
            if 'CI_PROJECT_URL' in os.environ:
                gitlab = os.environ['CI_PROJECT_URL'].strip('/')
                folder = base.split(args.root, 1)[1].strip('/')
                header = (
                    f" > Do not bother editing this page directly – it is automatically "
                    f"generated from [source]({gitlab}/blob/master/"
                    f"{folder}/{filename}).  Submit a merge request, instead!\n"
                )
                markdown = header + markdown

            markup = pypandoc.convert_text(markdown, f'{BIN}/confluence.lua', 'gfm')

            if args.dry_run:
                print("!! Would have updated %s, but --dry-run" % full_path, file=sys.stderr)
                print('----', file=sys.stderr)
                print(markup)
                print('----', file=sys.stderr)
            else:
                page = get_or_create_page(pagename, namespace)
                page = get_page_info(args.confluence_url, page['id'])

                # Check for unnecessary update first
                url = args.confluence_url + '/' + page['_links']['webui']
                digest = hashlib.sha256(markup.encode('utf-8')).hexdigest()
                if digest == page['version']['message']:
                    print("Skipping %s - no update needed." % url, file=sys.stderr)
                    continue

                # Otherwise, update our page with the output
                print("Updating %s" % url, file=sys.stderr)
                update_page(args.confluence_url, page['id'], markup, digest)
                print("Updated %s" % url, file=sys.stderr)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    args = getargs()

    publish(args)
