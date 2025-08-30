import requests
import json
from hunter_how.api_key import get_api_key
import base64
import time

class APIException(Exception):
	def __init__(self, code, message):
		super().__init__(message)
		self.code = code
		self.message = message
	def __str__(self):
		return f"{self.code}: {self.message}"

class HunterSearch():
	"""
	Class to handle search operations with Hunter.how API.
	"""

	def __init__(self, query, start_time, end_time, page, page_size, page_range, limit, fields, output=None, api_key=None):
		self.query = query
		self.start_time = start_time
		self.end_time = end_time
		self.page = page
		self.page_size = page_size
		self.page_range = page_range
		if page_range:
			self.page_range = self.validate_page_range(page_range)
   
		self.validate_page_size(page_size)
		self.limit = limit
		self.fields = fields
		self.validate_fields(fields)
		self.output = output
		self.api_key = api_key or get_api_key()
		if not self.api_key:
			raise ValueError("API key is required. Use --api-key or set it with 'hunter_how set_api_key <key>'.")
		

	def validate_page_range(self, page_range):
		if isinstance(page_range, int):
			return [1, page_range]
		elif isinstance(page_range, str):
			ranges = page_range.split('-')
			if len(ranges) == 1:
				return [1, int(ranges[0])]
			elif len(ranges) == 2 and int(ranges[1]) >= int(ranges[0]):
				return [int(ranges[0]), int(ranges[1])]
		raise ValueError("Invalid page range format. Use 'start-end' or just 'end'.")

	def validate_page_size(self, page_size):
		available_page_sizes = [10, 20, 50, 100, 1000]
		if page_size not in available_page_sizes:
			raise ValueError(f"Invalid page size. Available options: {', '.join(map(str, available_page_sizes))}.")

	def validate_fields(self, fields):
		available_fields = ["product", "transport_protocol", "protocol", "banner", "country", "province", "city", "asn", "org", "web", "updated_at"]
		if fields:
			fields = fields.split(",")
			for field in fields:
				if field not in available_fields:
					raise ValueError(f"Invalid field '{field}'. Available fields: {', '.join(available_fields)}.")

	def make_query(self):
		params = {
			"query": base64.b64encode(self.query.encode()).decode(),
			"start_time": self.start_time,
			"end_time": self.end_time,
			"page": self.page,
			"page_size": self.page_size,
			"api-key": self.api_key
		}
		
		if self.fields:
			params["fields"] = self.fields

		url = "https://api.hunter.how/search"
		response = requests.get(url, params=params)

		if response.status_code != 200:
			raise Exception(f"Error: {response.status_code} - {response.text}")

		resp = response.json()
		if "code" not in resp:
			raise Exception("Unexpected response format. 'code' field is missing in the response.")

		if "data" not in resp:
			raise APIException(resp["code"], f"'data' field is missing in the response. Perhaps the query is malformed. {resp.get('message')}")
		
		if resp["code"] != 200:
			raise APIException(resp["code"], resp.get('message', 'Unknown error'))

		return resp

	def execute(self):
		"""
		Execute the search and return results.
		"""
		if not self.page_range and not self.limit:
			result = self.make_query()
   
		elif self.page_range or self.limit:
			result = {}
			if self.page_range:
				rng = range(self.page_range[0], self.page_range[1] + 1)
			elif self.limit:
				rng = range(1, (self.limit // self.page_size) + 2)
			for page in rng:
				try:
					self.page = page
					page_data = self.make_query()
					code = page_data["code"]
					if result == {}:
						result = page_data
					else:
						if self.output: #don't spam to stdout if piping
							print(f"Got {len(page_data['data']['list'])} results..")

						result["data"]["list"].extend(page_data["data"]["list"])
						result["data"]["per_day_search_limit"] = page_data["data"]["per_day_search_limit"]
						result["data"]["per_day_search_count"] = page_data["data"]["per_day_search_count"]
						result["data"]["per_day_api_pull_limit"] = page_data["data"]["per_day_api_pull_limit"]
						result["data"]["per_day_api_pull_count"] = page_data["data"]["per_day_api_pull_count"]
				except APIException as e:
					if e.code == 440 and self.output:
						print("No more results available, ending search.")
					elif self.output:
						print(f"Error on page {page}: {e}")
					if "data" in result and "list" in result["data"]:
						print(f"Total results retrieved: {len(result['data']['list'])}")
					else:
						print("No results retrieved.")
						print(f"Error: {e}")
						return
  
				time.sleep(2) #to avoid rate limiting

		result["data"]["list"] = result["data"]["list"][:self.limit] if self.limit else result["data"]["list"]
		if self.output:
			with open(self.output, 'w') as f:
				json.dump(result, f, indent=4)
			print(f"{len(result['data']['list'])} results saved to {self.output}")
		else:
			print(json.dumps(result, indent=4))
