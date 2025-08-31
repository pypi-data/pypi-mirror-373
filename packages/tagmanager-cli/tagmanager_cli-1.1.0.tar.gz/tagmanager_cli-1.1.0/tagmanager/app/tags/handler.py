from .service import list_all_tags, search_files_by_tag, open_list_files_by_tag_result


def handle_tags_command(args):
    if args.search and args.open:
        open_list_files_by_tag_result(
            search_files_by_tag(args.search, args.exact)
        )
    elif args.search:
        result = search_files_by_tag(args.search, args.exact)
        for i, file in enumerate(result, start=1):
            print(f"{i}. {file}")
    else:
        for i, tag in enumerate(list_all_tags(), start=1):
            print(f"{i}. {tag}")
