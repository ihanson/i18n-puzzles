def is_valid_password(password):
	return (
		(4 <= len(password) <= 12)
		and any(char.isdigit() for char in password)
		and any(char.isupper() for char in password)
		and any(char.islower() for char in password)
		and any(ord(char) > 127 for char in password)
	)

if __name__ == "__main__":
	with open("03\\input.txt", encoding="utf-8") as in_file:
		print(sum(
			is_valid_password(line.strip())
			for line in in_file.readlines()
		))