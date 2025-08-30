import json

def parse(json_file, fields, delimiter, output_file=None, header=False):
	"""
	Parse a JSON file with results and print specified fields.
	
	Args:
		json_file (str): Path to the JSON file to parse.
		fields (str): Comma-separated list of fields to output. If None, all fields are printed.
	"""
 
	if output_file:
		out_file = open(output_file, 'w')
 
	def write(text):
		if output_file:
			out_file.write(text + "\n")
		else:
			print(text)

	with open(json_file, 'r') as file:
		data = json.load(file)["data"]["list"]
	if not fields:		
		fields = data[0].keys()
	else:
		fields = fields.split(",")
	for i, field in enumerate(fields):
		fields[i] = field.replace(delimiter, f"\\{delimiter}") #escape delimiter

	if header:
		write(delimiter.join(fields))

	for item in data:
		output = []
		for field in fields:
			if field in item:
				field_str = str(item[field])
				field_str = field_str.replace(delimiter, f"\\{delimiter}") 
				output.append(field_str)
		write(delimiter.join(output))

	if output_file:
		out_file.close()
