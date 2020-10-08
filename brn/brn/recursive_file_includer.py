
import re,os

def include_regex_match(l):
	return re.match(r"^@include (.*)", l)

def is_include_line(l):
	# we should probably throw if the line is just "@include" or is similarly malformed.
	return l.startswith('@include')

def do_includes(path):
	result = []
	for l in open(path).readlines():
		if is_include_line(l):
			match = include_regex_match(l)
			# hmm..
			included_file_path = os.path.dirname(path) + '/' + match.groups()[0]
			result += do_includes(included_file_path)
		else:
			result.append(l)
	return result

