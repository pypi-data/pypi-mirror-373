from .service import add_tags


def handle_add_command(args):
    add_tags(args.file, args.tags)