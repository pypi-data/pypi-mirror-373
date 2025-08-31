from .service import show_storage_location, open_storage_location


def handle_storage_command(args):
    if args.open:
        open_storage_location()
    else:
        print(show_storage_location())