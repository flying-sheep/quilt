#!/usr/bin/env python3

import subprocess
import sys

import pkg_resources

try:
    from pip._internal import main as pipmain
except ImportError:
    from pip import main as pipmain

import yaml

# To push out and use a new version of pydocmd to people generating docs,
# increment this here and in the quilt pydocmd repo (setup.py and __init__.py)
EXPECTED_VERSION_SUFFIX = '-quilt3'

# Github HTTPS Revision
# Just the branch name right now, but anything following '@' in a github repo URL
GH_HTTPS_REV = 'quilt'
GH_URL = f'git+https://github.com/quiltdata/pydoc-markdown.git@{GH_HTTPS_REV}'


def generate_cli_api_reference_docs():
    # This script relies on relative paths so it should only run if the cwd is gendocs/
    subprocess.check_call(["./gen_cli_api_reference.sh"])


def gen_walkthrough_doc():
    # This script relies on relative paths so it should only run if the cwd is gendocs/
    subprocess.check_call(["./gen_walkthrough.sh"])


def install_pydocmd():
    try:
        pydocmd_dist = pkg_resources.get_distribution('pydoc-markdown')  # install name, not module name
        version = pydocmd_dist.version
    except pkg_resources.DistributionNotFound:
        version = ''

    if not version.endswith(EXPECTED_VERSION_SUFFIX):
        valid_input = ['y', 'n', 'yes', 'no']
        response = ''

        while response not in valid_input:
            print("\nUsing {!r}:".format(sys.executable))
            if version:
                print("This will uninstall the existing version of pydoc-markdown ({}) first."
                      .format(version))
            sys.stdout.flush()
            sys.stderr.flush()
            response = input("    Install quilt-specific pydoc-markdown? (y/n): ").lower()

        if response in ['n', 'no']:
            print("exiting..")
            exit()

        if version:
            pipmain(['uninstall', 'pydoc-markdown'])

        print(f'Installing {GH_URL}')
        pipmain(['install', GH_URL])


if __name__ == "__main__":
    # CLI and Walkthrough docs uses custom script to generate documentation markdown, so do that first
    generate_cli_api_reference_docs()
    gen_walkthrough_doc()
    install_pydocmd()

    import pydocmd

    if not pydocmd.__version__.endswith(EXPECTED_VERSION_SUFFIX):
        print("Please re-run this script to continue")
        exit()

    from pydocmd.__main__ import main as pydocmd_main

    # hacky, but we should maintain the same interpreter, and we're dependent on how
    # pydocmd calls mkdocs.
    if sys.argv[-1].endswith('build.py'):
        print("Using standard args for mkdocs.")
        sys.argv.append('build')
    else:
        print("Using custom args for mkdocs.")

    print("\nStarting pydocmd_main...")

    pydocmd_main()

    print("...finished pydocmd_main")

    # report where stuff is
    with open('pydocmd.yml', encoding='utf-8') as f:
        pydocmd_config = yaml.safe_load(f)
    print("Generated HTML in {!r}".format(pydocmd_config.get('site_dir')))
    print("Generated markdown in {!r}".format(pydocmd_config.get('gens_dir')))
