use_test = True

def run(lines):
	print(sum(is_valid_password(line.strip()) for line in lines))

def is_valid_password(password):
	return (
		(4 <= len(password) <= 12)
		and any(char.isdigit() for char in password)
		and any(char.isupper() for char in password)
		and any(char.islower() for char in password)
		and any(ord(char) > 127 for char in password)
	)

#region Common code
if __name__ == "__main__":
	import pathlib
	input_path = pathlib.Path(__file__).parent.joinpath("test-input.txt" if use_test else "input.txt")
	with open(input_path, encoding="utf-8") as in_file:
		run(line.strip() for line in in_file)
#endregion