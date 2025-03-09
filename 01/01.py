use_test = False

def run(lines):
	print(sum(cost(line) for line in lines))

def is_valid_sms(text):
	return len(text.encode("utf-8")) <= 160

def is_valid_tweet(text):
	return len(text) <= 140

def cost(text):
	is_sms = is_valid_sms(text)
	is_tweet = is_valid_tweet(text)
	return (
		13 if is_sms and is_tweet
		else 11 if is_sms
		else 7 if is_tweet
		else 0
	)

#region Common code
if __name__ == "__main__":
	import pathlib
	input_path = pathlib.Path(__file__).parent.joinpath("test-input.txt" if use_test else "input.txt")
	with open(input_path, encoding="utf-8") as in_file:
		run(line.strip() for line in in_file)
#endregion
