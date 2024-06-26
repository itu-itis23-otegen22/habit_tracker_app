# Samurai's Discipline

This is console-based Habit Tracker application, which allows users to write down habits (or to do tasks) and helps with sticking to them. The app is written solely in Python and includes the following **functionalities** and **features**:
1. User Authentication (registration and log in)
2. Encryption of passwords and names of files
3. User's Manual
4. Menu that displays table of habits and recent days
5. Adding, Updating, Deleting habits
6. Variety of progress statistics of the user (4 graphs)
7. Settings of account and displayed table

Other technical details:
1. The app solely relies on CSV files for storing data
2. Binary search for finding the username
3. Advanced custom Caesar Encryption method
4. Validations (password, username, etc)




## How to Use?

1. Unzip zipped folder
2. Find "main.py" file inside "src" folder
3. Open the app with native console of the Windows OS (cmd) by double clicking.
4. Use the app in fullscreen mode in order to avoid any displaying issues.
5. (Only 3 files are needed for the app to run properly, which are "main.py", "new_menu.py", "functions.py".
Other files are saved in the project app in order to provide example users and habits with history.)

When the app is opened, welcoming page will be seen as below, where you can register or log in:
![Welcome page](./src/images/welcome_page.png)

--- You can register as a new user, but you will have to add habits and you will have no progress history to visualize. That is why, you can log in to existing account with some history.
Account details:
username: gatsby
password: Gatsby1!

--- When you log in, you can see the following menu page, where your current habits and recent days are shown.
![Menu page](./src/images/menu.png)

You have variety of options there, also you can enter the ID of the habit in the table in order to change its value for today.

You can add a habit by entering "a" or "add". Same applies to other options too.

--- For example, we can update a habit by entering "u" or "update":
![Update page](./src/images/habit_update.png)

--- Or you can go into settings and change your account details or displayed table related instance:
![Settings page](./src/images/settings.png)

--- You can see your performance for last week and last month for each habit, or general average progress for last 6 weeks or monthes:
![Progress Graphs](./src/images/graphs.png)

--- You can try all other functionalities available there. 50% of the time was spent for testing and debugging in order to minimize the possibility of logical errors.
When changing the details of accounts or habits, corresponding changes in CSV files also happen. Everything should be consistent and coherent.


## Requirements
1. Windows 10 or 11
2. Python version in my PC was 3.12


## Find a Bug

If you found any bug, or have some feedback on how to improve the product, you can fill out the [The Google Forms](https://docs.google.com/forms/d/e/1FAIpQLSe5HqEexhwNmDsihB1Ipqanh7TqP5CdyXhxgm49ocS7fBPE4A/viewform?usp=sf_link).

## 👋🏻


