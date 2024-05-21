import pandas as pd # for dataframes and csv
import time # time delays
import os # files and console access
import random # quotes randomizer

# user's Menu
from new_menu import *
# my additional custom functions file
from functions import *


# --- Creating users.csv if does not exist
# It will contain user information as name, username, and password
if not os.path.exists('users.csv'):
	data = {'name': [], 'username': [], 'psw': []}
	df = pd.DataFrame(data)
	df.to_csv('users.csv', header=True, index=False)

# --- Shortcut function to get users.csv as datafram
def users_df():
	if os.path.getsize('users.csv') == 0:
		data = {'name': [], 'username': [], 'psw': []}
		return pd.DataFrame(data)
	else:
		return pd.read_csv('users.csv')

# ---------------------------------------------------------------------  Intro function
def intro():
	print2('\n\t', ending='')
	quotes_df = pd.read_csv('quotes.csv')
	random_row = quotes_df.sample()
	author = random_row['author'].values[0]
	quote = random_row['quote'].values[0]
	print2(f'"{quote}" — {author}', ending='')
	time.sleep(2)

# ---------------------------------------------------------------------  Main function
def start():
	username = ""
	while True:
		clear()
		print("""
		**********************************
		*  Welcome to Habit Tracker app  *
		*      Samurai's Discipline      *
		**********************************

		1 - Register
		2 - Log in
		3 - User's manual
		4 - Exit
		""")
		username = ""
		x = input("---> ").lower().strip()
		
		if x == "1" or "register" in x:
			username, key = register()
			if len(username) > 0:
				menu(username, key) 
		elif x == "2" or "log" in x:
			username, key = login()
			if len(username) > 0:
				menu(username, key) 
		elif x == "3" or "manual" in x:
			user_manual()
		elif x == "4" or "exit" in x:
			exiting()
		else:
			print2("Please enter a valid option.\n(A number between 1 and 4)")
			enter()

# --------------------------------------------------------------------- User Manual
def user_manual():
	pass

# --------------------------------------------------------------------- Registration
def register():
	clear() # clearing console
	username = ""
	#-------------------------------------------- Taking user data
	while True:
		name = input("Your name?     ---> ")
		if len(name) > 0:
			break
	while True:
		username = input("Your username? ---> ")
		if not validate_username(username):
			print2("Username can contain only letters, digits, and underscore(_)!")
		else:
			if len(username) > 0:
				break

	# Checking if such username already exits
	df = users_df()
	if len(df) > 0:
		index = binary_search(df, username, 0, len(df) - 1)
	else:
		index = -1

	if index != -1:
		print2(f"\nUsername '{username}' already exists. Please choose a different one or Log in.")
		enter()
		return "", ""
	# --------------------- Password validation
	while True:
		psw = input("Your password? ---> ")
		if len(psw) >= 8 and any(i.isupper() for i in psw) and any(i.isdigit() for i in psw):
			break
		else:
			print2("Password must be at least 8 characters, and contain at least one uppercase letter and one digit")
			time.sleep(1)

	# Encrypting the password
	key = calculate_key(name)
	psw = encrypt_password(psw, key, caesar_digits)

	new_user = pd.DataFrame([{'name': name, 'username': username, 'psw': psw}], index=[index])

	# Finding where to insert a new user (Alphabetical order)
	index = 0
	while index < len(df) and df.iloc[index]['username'] < username:
		index += 1
	# Inserting data
	df = pd.concat([df.iloc[:index], new_user, df.iloc[index:]]).reset_index(drop=True)
	df.to_csv('users.csv', index=False)

	#----------------------------------------- Creating csv file for habits of this user
	# Encrypting the username 
	username = encrypt_username(username, key, caesar_digits, shift_string)
	# Creating name of csv file for the username
	filename = f'{username}.csv'

	if not os.path.exists('habits'):
		os.makedirs('habits')

	if not os.path.exists(f'habits/{filename}'):
		data = {'habit': [],
				'description': [], 
				'frequency': [],
				'start': [],
				'end': [],
				'accomplishment': []
				}
		df = pd.DataFrame(data)
		df.to_csv(f'habits/{filename}', header=True, index=False)

	# Registration finished
	print2(f"User named {name} is successfully registered!")
	enter()
	return username, key

# ------------------------------------------------------------------- Log in
def login():
	clear() # clearing the console
	username = ""
	df = users_df() #

	username = input("Your username? ---> ")
	index = binary_search(df, username, 0, len(df) - 1)
	if index == -1:
		print2("\nNo user found with that username.")
		enter()
		return "",""

	psw = input("Your password? ---> ")
	key = calculate_key(df.iloc[index]['name'])
	if decrypt_password(df.iloc[index]['psw'], key, caesar_digits) == psw:
		print2("Successfully Logged in!") 
		time.sleep(1)
		username = encrypt_username(username, key, caesar_digits, shift_string)
		return username, key
	else:
		print2("Incorrect Password!")
		enter()
	return "",""


#-------------------------------------------------------------- Initializing quotes.csv file
def quotes():
	# if quotes.csv already exists do nothing
	if os.path.exists('quotes.csv'):
		return
	else:
		# All available quotes
		quotes = [
			["Frank Ocean", "Work hard in silence, let your success be your noise."],
			["Bum Phillips", "The only discipline that lasts is self-discipline."],
			["Thomas Jefferson", "If you want something you have never had, you must be willing to do something you have never done."],
			["Neale Donald Walsch", "Life begins at the end of your comfort zone."],
			["Zig Ziglar", "You don’t have to be great to start, but you have to start to be great."],
			["James N. Watkins", "A river cuts through rock, not because of its power, but because of its persistence."],
			["Ryan Blair", "If it is important to you, you will find a way. If not, you’ll find an excuse."],
			["Tim Notke", "Hard work beats talent when talent doesn’t work hard."],
			["Confucius", "It does not matter how slowly you go as long as you do not stop."],
			["Karen Lamb", "A year from now you may wish you had started today."]
		]
		
		# Creating datafram from quotes list
		quotes_df_new = pd.DataFrame(quotes, columns=['author', 'quote'])
		# writing them to the quotes.csv file
		quotes_df_new.to_csv('quotes.csv', index=False)
		return

# Calling starting functions
quotes()
intro()
start()
