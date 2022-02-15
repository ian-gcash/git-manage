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
    if args.action == 'create_branch':
        print(f'Creating branch {args.to_} based on {args.from_}')
        create_branch(args.from_, args.to_, push_remote=args.remote)
    elif args.action == 'delete_branch':
        print(f'Deleting branch {args.from_}')
        delete_branch(args.from_, include_remote=args.remote)
    elif args.action == 'create_tag':
        print(f'Creating tag {args.tag_}')
        create_tag(args.from_, args.tag_, push_remote=args.remote)
    elif args.action == 'delete_tag':
        print(f'Deleting {args.tag_}')
        delete_tag(args.tag_, include_remote=args.remote)
    print('Done.')


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=[
        'create_branch',
        'delete_branch',
        'create_tag',
        'delete_tag'
    ])
    parser.add_argument(
        '--remote', '-R',
        help='Include or push to remote.',
        action='store_true',
        default=False
    )
    parser.add_argument(
        '--from', '-f',
        dest='from_',
        help='From branch or reference branch when deleting'
    )
    parser.add_argument(
        '--to', '-t',
        dest='to_',
        help='To or new branch when creating'
    )
    parser.add_argument(
        '--tag', '-a',
        dest='tag_',
        help='Tag to create or delete'
    )

    args = parser.parse_args()
    main(args)
