# CLI tool for Hunter.how
VER="1.0.0"

import datetime

def get_args():
	import argparse
	parser = argparse.ArgumentParser(description="⌖ Hunter.how CLI to search and parse results. Use --help on any subcommand for more information.")
	subparsers = parser.add_subparsers(dest='command', help='Available commands')

	# Define subcommands
	search_parser = subparsers.add_parser('search', help='search results by query.')
	year_ago = datetime.datetime.now() - datetime.timedelta(days=365)
	today = datetime.datetime.now()
	search_parser.add_argument("query", type=str, help="Search query.")
	search_parser.add_argument("--api-key", type=str, help="API key. If not specified, it will be loaded from the configuration file.")
	search_parser.add_argument("--start-time", type=str, default=year_ago.strftime("%Y-%m-%d"), help="Only show results after the given date (yyyy-mm-dd). Default is one year ago.")
	search_parser.add_argument("--end-time", type=str, default=today.strftime("%Y-%m-%d"), help="Only show results before the given date (yyyy-mm-dd). Default is today.")
	search_parser.add_argument("--page", type=int, default=1, help="Page number to retrieve. Default is 1.")
	search_parser.add_argument("--page-range", type=str, help="Retrieve several pages. Example: 2-4 will retrieve pages 2, 3 and 4. If the range start is not specified, it will start from 1: 3 will retrieve pages 1, 2, 3.")
	search_parser.add_argument("--limit", type=int, help="Retrieve up to this many results instead of manually using pagination.")
	search_parser.add_argument("--page-size", type=int, default=100, help="Number of results per page. Default is 100. Options: 10,20,50,100,1000.")
	search_parser.add_argument("--fields", type=str, help="Additional fields: product,transport_protocol,protocol,banner,country,province,city,asn,org,web,updated_at. Available for Professional and Professional Plus accounts only")
	search_parser.add_argument("-o", "--output", type=str, help="Output file name. If not specified, results will be printed to stdout.")
 
	set_api_parser = subparsers.add_parser('set_api_key', help='Set API key.')
	set_api_parser.add_argument("key", help="The API key.")

	parse_parser = subparsers.add_parser('parse', help='Parse a json file with hunter.how results.')
	parse_parser.add_argument("file", type=str, help="File to parse")	
	parse_parser.add_argument("-f", "--fields", type=str, help="Fields to output, comma-separated. If not specified, all fields are used.")
	parse_parser.add_argument("-o", "--output", type=str, help="Output file name. If not specified, results will be printed to stdout.")
	parse_parser.add_argument("-d","--delimiter", type=str, default=",", help="Delimiter for output fields. Default is comma.")
	parse_parser.add_argument("--header", action='store_true', help="Add header with field names (for CSV/TSV)")
	
	info_parser = subparsers.add_parser('info', help='Show information about this tool and configuration.')
 
	args = parser.parse_args()
	return args

def main():
	try:
		args = get_args()

		if args.command == 'search':
			if args.limit and args.page_range:
				raise ValueError("You cannot use both --limit and --page-range. Use one of them.")
			if args.limit and args.page!=1:
				raise ValueError("You cannot use both --limit and --page. Use one of them.")

			from hunter_how.search import HunterSearch
			hunter_search = HunterSearch(args.query, args.start_time, args.end_time, args.page, args.page_size, args.page_range, args.limit, args.fields, args.output, args.api_key)
			hunter_search.execute()
	
		elif args.command == 'set_api_key':
			from hunter_how.api_key import set_api_key
			set_api_key(args.key)

		elif args.command == 'parse':
			from hunter_how.parse import parse
			parse(args.file, args.fields, args.delimiter, args.output, args.header)

		elif args.command == 'info':
			from hunter_how.api_key import get_api_key
			print(f"Version: {VER}")
			print(f"API Key: {get_api_key() or 'Not set'}")
		
		else:
			print("Unknown command. Use --help for available commands.")
			exit(1)
	except Exception as e:
		print(f"Error: {e}")
		exit(1)
if __name__ == "__main__":
	main()
	