from .service import path_tags, fuzzy_search_path


def handle_path_command(args):
    if args.fuzzy:
        print(fuzzy_search_path(args.filepath))
    else:
        print(path_tags(args.filepath))