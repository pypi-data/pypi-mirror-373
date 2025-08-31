from .service import remove_path, remove_invalid_paths


def handle_remove_command(args):
    if args.path:
        remove_path(args.path)
    elif args.invalid:
        remove_invalid_paths()
    else:
        print("No arguments provided")
    return None