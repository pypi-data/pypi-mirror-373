from .service import combined_search, search_files_by_path, search_files_by_tags


def handle_search_command(args):
    if args.tags and args.path:
        # Combined search by tags and path
        result = combined_search(args.tags, args.path, args.match_all)
    elif args.tags:
        # Search by tags only
        result = search_files_by_tags(args.tags, args.match_all, args.exact)
    elif args.path:
        # Search by path only
        result = search_files_by_path(args.path)
    else:
        print("No search criteria provided.")
        print("Example: tm search -t python -p C:\\Users\\User\\Documents")
        print("Example: tm search -t python -t linux")
        print("Example: tm search -p C:\\Users\\User\\Documents")
        print("Example: tm search -p C:\\Users\\User\\Documents -p C:\\Users\\User\\Downloads")
        return

    if result:
        for i, file in enumerate(result, start=1):
            print(f"{i}. {file}")
        print()
    else:
        print("No files found matching the criteria.")


