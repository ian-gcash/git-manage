import subprocess
import sys

VERBOSE = True


def exec_cmd(cmd_args, verbose=False, exit_on_error=False):
    """Executes a command given a list of arguments
    
    :returns: CompletedProcess or CalledProcessError object

    """
    out = None
    
    try:
        out = subprocess.run(
            cmd_args, check=True, text=True, capture_output=True
        )
        
    except subprocess.CalledProcessError as e:
        out = e
        
    if out and verbose:
        # Combine results from stdout and stderr if it exists
        res = '\n'.join([i for i in (out.stdout, out.stderr) if i])
        print(f'{res}')
        
    if out and exit_on_error and out.returncode != 0:
        sys.exit(out.returncode)

    return out


def get_current_branch():
    """Returns current branch name"""
    out = exec_cmd(['git', 'status'], exit_on_error=True)
    # Get the last value from the first line
    return out.stdout.split('\n')[0].split()[-1]


def create_branch(from_branch, new_branch, push_remote=False):
    current_branch = get_current_branch()

    # Switch to base branch
    exec_cmd([
        'git', 'checkout', from_branch
    ], verbose=VERBOSE, exit_on_error=True)

    # Create new branch
    exec_cmd([
        'git', 'checkout', '-b', new_branch
    ], verbose=VERBOSE, exit_on_error=True)

    # Sync to remote
    if push_remote:
        exec_cmd([
            'git', 'push', '-u', 'origin', new_branch
        ], verbose=VERBOSE, exit_on_error=True)

    # Switch back original branch
    exec_cmd([
        'git', 'checkout', current_branch
    ], verbose=VERBOSE, exit_on_error=True)


def delete_branch(branch_name, include_remote=False):
    # Attempt to delete local branch
    exec_cmd([
        'git', 'branch', '-D', branch_name
    ], verbose=VERBOSE)

    # Attempt to delete remote branch
    if include_remote:
        exec_cmd([
            'git', 'push', 'origin', '--delete', branch_name
        ], verbose=VERBOSE)


def create_tag(from_branch, new_tag, push_remote=False):
    current_branch = get_current_branch()
    
    # Switch to branch to be tagged
    exec_cmd([
        'git', 'checkout', from_branch
    ], verbose=VERBOSE, exit_on_error=True)

    # Create new tag
    exec_cmd([
        'git', 'tag', new_tag
    ], verbose=VERBOSE, exit_on_error=True)

    # Sync to remote
    if push_remote:
        exec_cmd([
            'git', 'push', '-u', 'origin', new_tag
        ], verbose=VERBOSE, exit_on_error=True)

    # Switch back original branch
    exec_cmd([
        'git', 'checkout', current_branch
    ], verbose=VERBOSE, exit_on_error=True)


def delete_tag(tag_name, include_remote=False):
    # Attempt to delete local branch
    exec_cmd([
        'git', 'tag', '-d', tag_name
    ], verbose=VERBOSE)

    # Attempt to delete remote branch
    if include_remote:
        exec_cmd([
            'git', 'push', '--delete', 'origin', tag_name
        ], verbose=VERBOSE)

def main(args):
    if args.resource == 'branch' and args.action == 'create':
        print(f'Creating branch {args.to_} based on {args.from_}')
        create_branch(args.from_, args.to_, push_remote=args.remote)
    elif args.resource == 'branch' and args.action == 'delete':
        print(f'Deleting branch {args.from_}')
        delete_branch(args.from_, include_remote=args.remote)
    elif args.resource == 'tag' and args.action == 'create':
        print(f'Creating tag {args.tag_}')
        create_tag(args.from_, args.tag_, push_remote=args.remote)
    elif args.resource == 'tag' and args.action == 'delete':
        print(f'Deleting {args.tag_}')
        delete_tag(args.tag_, include_remote=args.remote)
    print('Done.')

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(
        dest='resource',
        help='Either branch or tag', 
        required=True)

    # Create parsers for resource = tag

    tag = subparsers.add_parser('tag')
    tag.add_argument('action', 
        choices=['create', 'delete'])
    tag.add_argument(
        '--remote', '-R',
        help='Include or push to remote.',
        action='store_true',
        default=False
    )
    tag.add_argument(
        '--from', '-f',
        dest='from_',
        help='From branch or reference branch when deleting'
    )
    tag.add_argument(
        '--tag', '-a',
        dest='tag_',
        help='Tag to create or delete'
    )

    # Create parsers for resource = branch
    branch = subparsers.add_parser('branch')
    branch.add_argument('action', 
        choices=['create', 'delete'])
    branch.add_argument(
        '--remote', '-R',
        help='Include or push to remote.',
        action='store_true',
        default=False
    )
    branch.add_argument(
        '--from', '-f',
        dest='from_',
        help='From branch or reference branch when deleting'
    )
    branch.add_argument(
        '--to', '-t',
        dest='to_',
        help='To or new branch when creating'
    )

    args = parser.parse_args()
    main(args)
