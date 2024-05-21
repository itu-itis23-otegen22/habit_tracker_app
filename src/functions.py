import pandas as pd # for dataframes and csv
import time # time delays
import os # files and console access
import random # quotes randomizer
from datetime import date, datetime
import re # regex for username validation

# --- Clear console function
def clear():
	os.system('cls' if os.name == 'nt' else 'clear')


# --- Smooth typing of text
def print2(text, ending="\n"):
	for i in text:
		time.sleep(0.02)
		print(i, end="", flush=True)
	print(ending, end='')

# ------ Press Enter to continue
def enter():
	print2("- - - Press Enter to continue - - -")
	input()

# --------------------------------- Username validation function
def validate_username(username): # i am using regex pattern from re library
	pattern = r'^\w+$'
	if re.match(pattern, username):
		return True
	else:
		return False

#------------------------------------------------------------ Binary Search (recursive)
def binary_search(df, target, left, right):
	if right >= left:
		mid = left + (right - left) // 2

		if df.iloc[mid]['username'] == target:
			return mid
		elif df.iloc[mid]['username'] > target:
			return binary_search(df, target, left, mid - 1)
		else:
			return binary_search(df, target, mid + 1, right)
	else:
		return -1


# ----------------- Function to print randomly chosen quote, and EXIT
def exiting():
	quotes_df = pd.read_csv('quotes.csv')
	random_row = quotes_df.sample()
	author = random_row['author'].values[0]
	quote = random_row['quote'].values[0]
	print2(f'"{quote}" — {author}')
	time.sleep(1)
	print2("We hope to see you again soon. Have a great day!")
	time.sleep(1)
	print2("exiting...", ending='')
	exit()



# --------------------------------------------------------------------- Password Encryption
# list of random digits that will be used for advanced caesar cipher
caesar_digits = "9760168424257900908756324659617588019838122741889620518377411759557692490655041112104398116471008803733779368763614019245127272968492959860489206470774375379724625383091685542889532371109164605603059735473298998132143587895127068861932267845525018780471766"
def calculate_key(name): # I generate key from the name of the user
	first_ascii = ord(name[0])
	middle_ascii = ord(name[len(name) // 2])
	key = middle_ascii * (len(name) + first_ascii) + len(name) + 11 # some random weird formula hard to find out from statistical analysis
	return key

def encrypt_password(text, key, caesar_digits):
	encrypted = ''
	caesar_digits_length = len(caesar_digits)

	for i, char in enumerate(text):
		shift_index = (key + i) % caesar_digits_length
		shift_amount = int(caesar_digits[shift_index]) # shift amount is random in my case, not permanent
		shifted_char = chr((ord(char) + shift_amount) % 256) # character is shifted in ascii codes
		encrypted += shifted_char

	return encrypted

def decrypt_password(encrypted, key, caesar_digits):
	decrypted_text = ''
	caesar_digits_length = len(caesar_digits)

	for i, char in enumerate(encrypted):
		shift_index = (key + i) % caesar_digits_length
		shift_amount = int(caesar_digits[shift_index])
		shifted_char = chr((ord(char) - shift_amount) % 256) # here is we should substract
		decrypted_text += shifted_char

	return decrypted_text

# --------------------------------------------------------------------- Username Encryption
# String of characters used for shifting
shift_string = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_"
# in username encryption, I used this string because username can contain only letters, digits, and underscore
def encrypt_username(text, key, caesar_digits, shift_string): # the algorithm is same, only I use my own string instead of ascii table
	encrypted = ''
	shift_string_length = len(shift_string)
	caesar_digits_length = len(caesar_digits)

	for i, char in enumerate(text):
		if char in shift_string:
			shift_index = (key + i) % caesar_digits_length
			shift_amount = int(caesar_digits[shift_index])
			original_index = shift_string.index(char)
			shifted_index = (original_index + shift_amount) % shift_string_length
			encrypted += shift_string[shifted_index]
		else:
			encrypted += char

	return encrypted
def decrypt_username(encrypted, key, caesar_digits, shift_string):
	decrypted_text = ''
	shift_string_length = len(shift_string)
	caesar_digits_length = len(caesar_digits)

	for i, char in enumerate(encrypted):
		if char in shift_string:
			shift_index = (key + i) % caesar_digits_length
			shift_amount = int(caesar_digits[shift_index])
			original_index = shift_string.index(char)
			shifted_index = (original_index - shift_amount) % shift_string_length
			decrypted_text += shift_string[shifted_index]
		else:
			decrypted_text += char

	return decrypted_text
