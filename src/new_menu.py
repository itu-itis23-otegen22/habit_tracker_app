import pandas as pd # for dataframes and csv
import time # time delays
import os # files and console access
import random # quotes randomizer
from datetime import date, datetime, timedelta
from tabulate import tabulate
import matplotlib.pyplot as plt
# My custom functions
from functions import *


#----------------------------------- Menu for user's account
def menu(username, key=""):
	filename = f'habits/{username}.csv' # file of the user where his/her habits' information are kept
	table_num_days = 5 # when displaying table, how many days before are shown
	while True:
		dec_username = decrypt_username(username, key, caesar_digits, shift_string) # decrypting the username
		table(username, table_num_days, key) # displaying the table
		options() # displaying the options
		print("\n")
		# Taking input command from the user
		command = input("---> ").lower().strip()
		if command.isdigit():	# check if the input is a digit
			try:	# to avoid any problems
				command = int(command)  # convert the input to  integer
			except:
				print2("Some error occured, my apologies! ")
			else:
				accomplish(username, command) # changing the value "DONE" or "X" for today
		elif command == "a" or "add" in command:
			add_habit(username)
		elif command == "u" or "update" in command:
			update_habit(username)
		elif command == "d" or "delete" in command:
			delete_habit(username)
		elif command == "p" or "progres" in command or "report" in command:
			progress_report(username)
		elif command == "s" or "setting" in command:
			setting, num_days = settings(username, key)
			if 1 <= num_days <= 7:
				table_num_days = num_days 
			if setting: # if some information about user was changed, return to the main function
				return
		elif command == "e" or "exit" in command:
			exiting()
		else:
			print2("Please enter a valid option!")
			time.sleep(1)

#----------------------------------- Accomplishing the habit
def accomplish(username, command): # function to change the value "DONE" or "X" for today in the table
	filename = f'habits/{username}.csv'
	today = datetime.today().date()

	try:
		df = pd.read_csv(filename)
	except FileNotFoundError:
		print2("No habits found for this user.")
		time.sleep(1)
		return

	# Since in the table, habits that ended are not shown, their ID is different than in CSV file,
	# so, I should take id from the displayed table

	# Creating a list of displayed habits
	displayed_habits = []
	for i, row in df.iterrows():
		start_date = datetime.strptime(row['start'], '%y-%m-%d').date()
		end_date = datetime.strptime(row['end'], '%y-%m-%d').date()
		if today <= end_date:  # Only consider habits that have not ended
			displayed_habits.append(i)

	if command < 1 or command > len(displayed_habits):
		print2(f"Invalid habit ID. Enter integer between 1 and {len(displayed_habits)}.")
		time.sleep(1)
		return

	# Geting the correct habit index
	habit_index = displayed_habits[command - 1]
	habit = df.loc[habit_index]
	start_date = datetime.strptime(habit['start'], '%y-%m-%d').date()
	end_date = datetime.strptime(habit['end'], '%y-%m-%d').date()

	# Checking if todays date is between the start and end date
	if today < start_date or today > end_date:
		print2("Today's date is outside the range of this habit.")
		time.sleep(1)
		return

	# Calculating today index in the accomplishment string
	index = (today - start_date).days
	accomplishment = list(habit['accomplishment'])

	# Now, we switch between "DONE" and "X" (if the task is accomplished today or not)
	if accomplishment[index] == 'F':
		accomplishment[index] = 'T'
	else:
		accomplishment[index] = 'F'

	# Updating the dataframe, adn saving it to the csv 
	df.at[habit_index, 'accomplishment'] = ''.join(accomplishment)
	df.to_csv(filename, index=False)



#----------------------------------- Displaying habits progress table
def settings(username, key):
	clear()
	filename = f'habits/{username}.csv'

	if os.path.getsize('users.csv') == 0:
		data = {'name': [], 'username': [], 'psw': []}
		df = pd.DataFrame(data)
	else:
		df = pd.read_csv('users.csv')

	# Decrypting the username
	username = decrypt_username(username, key, caesar_digits, shift_string)
	# finding the user
	index = binary_search(df, username, 0, len(df) - 1)
	if index == -1:
		print2("\nNo information of given user!")
		enter()
		return 0, -1
	print("""
	1. Change Name
	2. Change Username
	3. Change Password
	4. Change number of displayed days
	5. Delete my Account
	6. Log Out
	7. <-- Back""")

	x = input("---> ").lower().strip()

	if x=='2' or 'user' in x: # ------------------------- Changing Username
		while True:
			new_username = input("Enter a new username ---> ")
			if len(df) > 0:
				ind = binary_search(df, new_username, 0, len(df) - 1)
			else:
				ind = -1
				
			if not validate_username(new_username):
				print2("Username can contain only letters, digits, and underscore(_)!")
			elif username == new_username:
				return 0, -1
			elif ind != -1:
				print2(f"\nUsername '{new_username}' already exists.")
			else:
				if len(username) > 0:
					break

		new_user = pd.DataFrame([{'name': df.iloc[index]['name'], 'username': new_username, 'psw': df.iloc[index]['psw']}], index=[index])

		# Finding where to insert a new user (Alphabetical order)
		insert = 0
		while insert < len(df) and df.iloc[insert]['username'] < new_username:
			insert += 1
		# Inserting data
		df = pd.concat([df.iloc[:insert], new_user, df.iloc[insert:]]).reset_index(drop=True)
		df.to_csv('users.csv', index=False)

		print2(f"Your username is updated to '{new_username}'.")
		# Encrypting the username
		key = calculate_key(df.iloc[insert]['name'])
		new_username = encrypt_username(new_username, key, caesar_digits, shift_string)
		os.rename(filename, f'habits/{new_username}.csv')

		# Deleting the previous username from users.csv
		old_user = binary_search(df, username, 0, len(df) - 1)
		if old_user >= 0:
			df = df.drop(old_user)
			df.to_csv('users.csv', index=False)
		

	elif x=='1' or 'name' in x: # ------------------------- Changing Name
		while True:
			new_name = input("Enter a new name? ---> ")
			if len(new_name) > 0:
				break

		# Since the encryption key depends on the name of the user,
		# First, we should change the password in users.csv file

		# Calculating old and new keys
		old_key = calculate_key(df.iloc[index]['name'])
		new_key = calculate_key(new_name)


		psw = decrypt_password(df.iloc[index]['psw'], old_key, caesar_digits) # decrypting password with old key
		enc_psw = encrypt_password(psw, new_key, caesar_digits) # encrypt it with new key
		df.loc[index, 'psw'] = enc_psw # changing password value in the dataframe

		# Second, we should change the user's habits csv file name
		enc_username = encrypt_username(df.iloc[index]['username'], new_key, caesar_digits, shift_string) # encrypt username with new key
		os.rename(filename, f'habits/{enc_username}.csv')

		# Finally, we change the name
		df.loc[index, 'name'] = new_name
		# And write the dataframe to users csv file
		df.to_csv('users.csv', index=False)
		print2(f"Your name is updated to '{new_name}'.")
	

	elif x=='3' or 'password' in x: # ------------------------- Changing Password
		while True:
			new_psw = input("Enter a new password? ---> ")
			if len(new_psw) >= 8 and any(i.isupper() for i in new_psw) and any(i.isdigit() for i in new_psw):
				break
			else:
				print2("Password must be at least 8 characters, and contain at least one uppercase letter and one digit")
				time.sleep(0.5)

		# Encrypting the password
		key = calculate_key(df.iloc[index]['name'])
		new_psw = encrypt_password(new_psw, key, caesar_digits)
		df.loc[index, 'psw'] = new_psw
		df.to_csv('users.csv', index=False)
		print2(f"Your password is updated!")

	elif x == '4' or 'number' in x or 'days' in x:
		table_num_days = input("How many days do you want the table to display? ---> ").strip()
		try:
			table_num_days = int(table_num_days)
		except:
			print2('Please enter an integer between 1-7')
			time.sleep(1)
			return 0, -1
		else:
			if not 1 <= table_num_days <= 7:
				print('Please enter an integer between 1-7')
				time.sleep(1)
				return 0, -1
			else:
				return 0, table_num_days


	elif x=='5' or 'delete' in x: # ------------------------- Deleting the account
		confirm = input("Are you sure you want to delete your account? (yes/no) ---> ").strip().lower()
		if confirm == "yes" or confirm == "y":
			df = df.drop(index) # Removing the user
			df.to_csv('users.csv', index=False) # updating the csv

			# Checking if the file exists, then delete it
			if os.path.exists(filename):
				os.remove(filename)
			print2("Your account has been deleted.")

		elif confirm == "no" or confirm == "n":
			print2("Your account was not deleted.")
			enter()
			return 0, -1
		else:
			print2("Invalid input. Please enter 'yes' or 'no'.")
			enter()
			return 0, -1


	elif x=='6' or 'out' in x: # ------------------------- logging out
		confirm = input("Are you sure you want to log out from your account? (yes/no) ---> ").strip().lower()

		if confirm == "yes" or confirm == "y":
			return 1, -1
		elif confirm == "no" or confirm == "n":
			return 0, -1
		else:
			print2("Invalid input. Please enter 'yes' or 'no'.")
			enter()
			return 0, -1

	elif x=='7' or 'back' in x: # ------------------------- Going Back
		return 0, -1

	else:
		print2("The option you provided is not valid.")
		time.sleep(1)
		return 0, -1
	enter()
	return 1, -1

#----------------------------------- Displaying habits progress table
def table(username, table_num_days = 5, key=""):
	clear()
	dec_username = decrypt_username(username, key, caesar_digits, shift_string)
	print(f"--- {dec_username} ---", end='\n\n')
	filename = f'habits/{username}.csv'
	try:
		df = pd.read_csv(filename)
	except FileNotFoundError:
		# creating new file if not found
		data = {'habit': [],
				'description': [],
				'frequency': [],
				'start': [],
				'end': [],
				'accomplishment': []
			   }
		df = pd.DataFrame(data)
		df.to_csv(filename, index=False)

	# Converting start and end dates bacj to datetime objects
	df['start'] = pd.to_datetime(df['start'], format='%y-%m-%d')
	df['end'] = pd.to_datetime(df['end'], format='%y-%m-%d')


	today = datetime.today().date() # getting today's date

	table_data = [] # creating empty list to store rows of the table that wil be shown

	# Iterating each habit in the dataframe
	for i, row in df.iterrows():
		habit_name = row['habit']
		accom = row['accomplishment']
		start_date = row['start'].date()
		end_date = row['end'].date()
		frequency = row['frequency']

		# Skipping habits if today is after their end date
		if today > end_date:
			continue
		
		# List for the habit's row
		idn = str(i+1)
		habit_row = [idn, habit_name]

		# Number of accomplishments for the last week
		last_week_start = today - timedelta(days=7)
		progress = 0

		for i in range(7):
			check_date = last_week_start + timedelta(days=i+1)
			if start_date <= check_date <= row['end'].date():
				index = (check_date - start_date).days
				if accom[index] == 'T':
					progress += 1

		
		# Calculating the date for each of the last n days
		for i in range(table_num_days):
			check_date = today - timedelta(days=i)
			if start_date <= check_date <= row['end'].date():
				# We should calculate index of the day in the accomplishment string
				index = (check_date - start_date).days
				if accom[index] == 'T':
					habit_row.append('DONE') # DONE when accomplished
				else:
					if progress >= frequency:
						# Two hyphens when task is not done for that day, but frequency goal for the week met
						habit_row.append('--') 
					else:
						habit_row.append("x") # X when not accomplished
			else:
				habit_row.append("nan")  # nan if days out of range

		# making sure each row has the same number of columns, which maybe unnessary, but just for case
		while len(habit_row) < table_num_days + 2:  # +2 for ID and habit columns
			habit_row.append("")

		# adding the habit row of the table
		table_data.append(habit_row)

	# Column headers in our table, that are always the same
	headers = ["id", "Habit", "Today"]

	for i in range(1, table_num_days): # adding days of week
		day_name = (today - timedelta(days=i)).strftime('%A')
		headers.append(day_name)

	# DIsplaying the table
	print(tabulate(table_data, headers=headers, tablefmt='grid'))
	print("\n")
#----------------------------------- Displaying habits information table
def print_habits(username):
	filename = f'habits/{username}.csv'
	try:
		df = pd.read_csv(filename)
	except FileNotFoundError:
		print2(f"No habits found for user '{username}'.")
		time.sleep(1)
		return
	clear()
	df.insert(0, 'ID', range(1, len(df) + 1))
	df.drop(columns=['accomplishment'], inplace=True)
	table = tabulate(df, headers='keys', showindex=False, tablefmt='grid')

	print(table)
#----------------------------------- Displaying options
def options():
	options = [
    ["", "a --> Add habit",       "", "", "", "Enter the corresponding"],
    ["", "u --> Update habit",    "", "", "", "id number of the habit"],
    ["", "d --> Delete habit",    "", "", "", "in order to change"],
    ["", "p --> Progress Report", "", "", "", "its today's value."],
    ["", "s --> Settings",        "", "", "", ""],
    ["", "e --> Exit",            "", "", "", ""]
    ]
	# Print the table without borders
	print(tabulate(options, tablefmt="plain"))


#----------------------------------- Adding a new habit
def add_habit(username):
	filename = f'habits/{username}.csv'

	try:
		df = pd.read_csv(filename)
	except FileNotFoundError:
		df = pd.DataFrame(columns=['habit', 'description', 'frequency', 'start', 'end', 'accomplishment'])

	#-------------------------------------------- Taking habit data
	print("Enter information about new habit:")
	name = input("Habit Name?     ---> ")
	if len(name) == 0:
		print2("Habit name cannot be empty!")
		time.sleep(1)
		return

	# Checking if such habit already exists
	index = -1
	if len(df) > 0:
		for i in range(len(df)):
			if df.iloc[i]['habit'].lower() == name.lower():
				index = i

	if index != -1:
		print2(f"\nHabit {name} already exists.")
		enter()
		return

	# Taking description of a habit
	desc = input("Habit Description? ---> ")

	# Taking frequency of the habit
	freq = 0
	while True:
		f = input(f"Please choose the frequency of the task.\nHow many times per week will you do '{name}'?\n(1 - once a week, 7 - every day)\n---> ").strip()

		if f.isdigit():	# check if the input is a digit
			try:	# to avoid any problems
				freq = int(f)	# convert the input to  integer
				if 1 <= freq <= 7:	# check if the integer is between 1 and 7
					break
			except:
				pass
		print("Invalid input. Please enter a valid integer between 1-7.")

	# start date is today
	start_date = date.today()
	start = start_date.strftime("%y-%m-%d")  # string date as YY-MM-DD

	# Taking end date
	while True:
		e = input("How many months are you planning to stick to that habit? ---> ")
		try:
			en = int(e)
		except:
			pass
		else:
			if en > 0 and en < 1201: # maximum is 1200 months, which is 100 years
				# Calculating the end date
				year = start_date.year
				month = start_date.month + en

				while month > 12:
					month -= 12
					year += 1

				end_date = date(year, month, start_date.day)
				end = end_date.strftime("%y-%m-%d")
				break
		print2("Enter a valid number of months!")
		time.sleep(1)

	# Accomplishment is F (not accomplished) for all days when the habit is created (T is accomplished)
	accom = ""
	num_days = (end_date - start_date).days + 1
	for i in range(num_days):
		accom += 'F'

	# ADD new habit data to the dataframe
	new_habit = pd.DataFrame({'habit': [name], 'description': [desc], 'frequency': [freq], 'start': [start], 'end': [end], 'accomplishment': [accom]})
	df = pd.concat([df, new_habit], ignore_index=True)

	# Saving the updated datafram to the csv file
	df.to_csv(filename, header=True, index=False)


#----------------------------------- Updating a Habit
def update_habit(username):
	filename = f'habits/{username}.csv'
	print_habits(username)

	try:
		df = pd.read_csv(filename)
	except FileNotFoundError:
		print("No habits found for this user.")
		return

	# Displaying ids and habits
	print("\nHabits:")
	for i, habit in df.iterrows():
		print(f"{i + 1}. {habit['habit']}")

	# taking input from user
	habit_id = input("Enter the ID of the habit you want to update (0 to cancel) ---> ").strip()
	if habit_id == '0':
		return

	# Validation of the input
	try:
		habit_id = int(habit_id)
		if habit_id < 1 or habit_id > len(df):
			print("Habit number is invalid")
			return
	except ValueError:
		print("Invalid input. Please enter a number.")
		return

	# Getting the habit that will be updated
	habit = df.loc[habit_id - 1]

	#-------------------------------------------- Taking habit data
	# Taking updated habit name
	name = input("Enter the updated habit name (leave blank to keep current name) ---> ").strip()
	if len(name) == 0:
		name = habit['habit']
	# Checking if such habit already exists
	else:
		index = -1
		for i in range(len(df)):
			if df.iloc[i]['habit'].lower() == name.lower():
				index = i
		if index != habit_id - 1 and index != -1: #-----------------------
			print2(f"\nHabit {name} already exists.")
			enter()
			return


	# Taking updated habit description
	desc = input("Enter the updated habit description (leave blank to keep current description) ---> ")
	if len(desc) == 0:
		desc = habit['description']

	# Taking updated frequency
	while True:
		freq = input("Enter the updated frequency (1-7 times per week, leave blank to keep current frequency) ---> ").strip()
		if len(freq) == 0:
			freq = habit['frequency']
			break
		else:
			if freq.isdigit() and 1 <= int(freq) <= 7:
				freq = int(freq)
				break
			else:
				print2("Invalid number. Enter number between 1 and 7.")

	# Start date is same as before
	start = habit['start']
	
	accomplishment = habit['accomplishment']
	# Taking updated end date
	while True:
		end_input = input("Enter the updated end date (YYYY-MM-DD, leave blank to keep current end date) ---> ").strip()
		if len(end_input) == 0:
			end = habit['end']
			break
		try:
			end_date = datetime.strptime(end_input, '%Y-%m-%d').date()
			if end_date > datetime.strptime(start, '%y-%m-%d').date():
				end = end_date.strftime('%y-%m-%d')

				current_end_date = datetime.strptime(habit['end'], '%y-%m-%d').date()
				num_days_new = (end_date - datetime.strptime(start, '%y-%m-%d').date()).days + 1
				num_days_current = (current_end_date - datetime.strptime(start, '%y-%m-%d').date()).days + 1

				if end_date > current_end_date:
					# Adding 'F's if the new end date is later
					accomplishment = habit['accomplishment'] + 'F' * (num_days_new - num_days_current)
				else:
					# Removing excess accomplishment data if the new end date is earlier
					accomplishment = habit['accomplishment'][:num_days_new]
				break
			else:
				print2("End date must be after start date.")
		except ValueError:
			print2("Invalid date format. Please enter the date in YYYY-MM-DD format.")


	# Updating the habit information
	df.loc[habit_id - 1] = [name, desc, freq, start, end, accomplishment]

	# Saving the updated datafrace to the csv file
	df.to_csv(filename, index=False)
	print2("Habit updated successfully.")
	time.sleep(1)


#----------------------------------- Deleting a Habit
def delete_habit(username):
	filename = f'habits/{username}.csv'
	if not os.path.exists(filename):
		print2("No habits found for this user.")
		time.sleep(1)
		return
	
	df = pd.read_csv(filename)

	# Displaying list of habits
	print("Habits:")
	for i, habit in df.iterrows():
		print(f"{i + 1}. {habit['habit']}")

	# User should input id the habit he/she wants to delete
	habit_id = input("Enter ID of the habit you want to delete (0 to cancel) ---> ")
	if habit_id == '0':
		return

	# Validating input from user
	try:
		habit_id = int(habit_id)
		if habit_id < 1 or habit_id > len(df):
			print2("Invalid habit ID.")
			time.sleep(1)
			return
	except ValueError:
		print2("Invalid input.")
		time.sleep(1)
		return

	# Confirmation
	habit_name = df.loc[habit_id - 1, 'habit']
	confirm = input(f"Are you sure you want to delete habit {habit_name}? (yes/no) ---> ").lower().strip()
	if confirm != 'y' and confirm != 'yes' and confirm != 'yeah' and confirm != 'yep':
		print2("Deletion canceled.")
		time.sleep(1)
		return

	# Deleting finally
	df.drop(habit_id - 1, inplace=True)

	# Updating the csv
	df.to_csv(filename, index=False)
	print2("Habit deleted successfully.")
	time.sleep(1)


#----------------------------------- Show progress function (matplotlib graphs)

def calculate_performance(accomplishment, start_date, end_date, frequency, period_days, real_start_date):
	# Calculating total days in the period
	total_days = (end_date - start_date).days + 1
	if total_days <= 0: # To prevent any issues with incorrect dates
		return 0
	# Finding the number of calculated days over given period of days
	completed_days = 0
	count = 0
	for i in range(min(total_days, period_days)): # min was used in order to calculate proper percentage when the week or month is not finished yet
		check_date = end_date - timedelta(days=i) # date when we will calculate the performance
		index = abs((check_date - real_start_date).days) # how many days from start date to that date
		
		if 0 <= index < len(accomplishment):
			count += 1
			if accomplishment[index] == 'T': # if that day this habit is DONE, then completed
				completed_days += 1

	if count == 0: # if something was out of range
		return 0.0011

	expected_days = (count / 7) * frequency # how many days expected to complete
	perf = 0
	if expected_days > 0:
		perf = (completed_days / expected_days) * 100 # calculating the performance
	return perf

def progress_report(username):
	filename = f'habits/{username}.csv'
	df = pd.read_csv(filename)

	# Converting start and end dates to datetime types
	df['start'] = pd.to_datetime(df['start'], format='%y-%m-%d')
	df['end'] = pd.to_datetime(df['end'], format='%y-%m-%d')

	today = datetime.today().date()
	last_week_start = today - timedelta(days=7)
	last_month_start = today - timedelta(days=30)

	# New list of last weekly and monthly performances
	last_week_performance = []
	last_month_performance = []

	# This is block of code to calculate last week and month perforemances for first two bar graphs
	for i, row in df.iterrows():
		start_date = row['start'].date()
		end_date = row['end'].date()
		frequency = row['frequency']
		accomplishment = row['accomplishment']

		# Adding last performances for each habit
		weekly_perf = calculate_performance(accomplishment, start_date, today, frequency, 7, start_date)
		last_week_performance.append(weekly_perf)

		# Doing same but for last month
		monthly_perf = calculate_performance(accomplishment, start_date, today, frequency, 30, start_date)
		last_month_performance.append(monthly_perf)

	# Next, we calculate performances for each of last 6 weeks and months, for last two line graphs
	weekly_dates = ["This week", "Last week", "2 weeks ago", "3 weeks ago", "4 weeks ago", "5 weeks ago"] # x axis labels
	week_averages = []

	for i in range(6): # we will display 6 weeks
		week_start = today - timedelta(days=7 * (i + 1))
		week_end = today - timedelta(days=7 * i)
		sum_perf = 0
		count = 0
		average = 0

		for _, row in df.iterrows():

			perf = calculate_performance(row['accomplishment'], week_start, week_end, row['frequency'], 7, row['start'].date())
			if perf == 0.0011: # if sth is wrong with range, skip this habit from considering
				continue
			if perf > 110: # if performance is very high, just take it as 110, to not affect much the average
				perf = 110
			sum_perf += perf
			count += 1

		average = sum_perf / count if count != 0 else 0 # to make sure nothing goes incorrect with list length
		week_averages.append(average)


	# Calculating general average performance for the last 6 months
	monthly_dates = [today.strftime("%B")] + [(today.replace(day=1) - timedelta(days=30 * i)).strftime("%B") for i in range(1, 6)]
	# Taking this and last 5 month names as list comprehension

	month_averages = []

	for i in range(6):
		month_start = (today.replace(day=1) - timedelta(days=30 * i)).replace(day=1) # taking 1st day of start month
		# taking the last day of the month or today, if month did not end
		month_end = (today.replace(day=1) - timedelta(days=30 * (i - 1))).replace(day=1) - timedelta(days=1) if i > 0 else today 
		sum_perf = 0
		count = 0
		average = 0

		for _, row in df.iterrows():
			perf = calculate_performance(row['accomplishment'], month_start, month_end, row['frequency'], 30, row['start'].date())
			if perf == 0.0011:
				continue
			if perf > 110:
				perf = 110
			sum_perf += perf
			count += 1

		average = sum_perf / count if count != 0 else 0
		month_averages.append(average)



	# ---------------------------------------------------------------- Plotting the graphs
	fig, axs = plt.subplots(2, 2, figsize=(14, 10))

	# Bar graph of last week performance
	axs[0, 0].bar(df['habit'], last_week_performance, color='blue')
	axs[0, 0].set_title("This Week's Performance")
	axs[0, 0].set_ylabel("Performance (%)")

	# Bar graph of last month performance
	axs[0, 1].bar(df['habit'], last_month_performance, color='green')
	axs[0, 1].set_title("This Month's Performance")
	axs[0, 1].set_ylabel("Performance (%)")

	# Line graf of last 6 weeks' average performance
	axs[1, 0].plot(weekly_dates, week_averages, marker='o', linestyle='-', color='red')
	axs[1, 0].set_title("Average Performance Over Last 6 Weeks")
	axs[1, 0].set_ylabel("Average Performance (%)")

	# Line graph of 6 months average performance
	axs[1, 1].plot(monthly_dates, month_averages, marker='o', linestyle='-', color='purple')
	axs[1, 1].set_title("Average Performance Over Last 6 Months")
	axs[1, 1].set_ylabel("Average Performance (%)")

	plt.tight_layout() # since i have 4 plots, lets display them in one window without overlapping
	plt.show()
