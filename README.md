# World Capitals Quiz
## created by Jake Feinbaum
  
A quiz to name all the capital cities of the world, built in PyQt5.

Instructions:
  1. Download and `cd` into this repository.
  2. If this is your first time using the application, run `python init_times.py` to initialize each of the elapsed times to 0.
  3. Run `python wcg.py` to start the quiz.
  4. Guess the capital of each randomly selected country until the entire table is filled.
 
`data.json` contains a dictionary used as an answer key and to store elapsed times:
	key: country name
	values:
		- display: capital city name displayed on the table
		- allowed: list of all permissible spellings of capital
		- time: average time elapsed for user to guess capital; updates each round

Answers are case insensitive.
