from datetime import datetime

MIN_HUMAN_YEAR = -9999
MAX_GUESSES = 8

hints = {5: {'color': 'black', 'min': 201, 'max': float('inf'), 'text': 'over 200 years off', 'emoji': '⬛'},
         4: {'color': 'brown', 'min': 41, 'max': 200, 'text': '41-200 years off', 'emoji': '🟫'},
         3: {'color': 'red', 'min': 11, 'max': 40, 'text': '11-40 years off', 'emoji': '🟥'},
         2: {'color': 'orange', 'min': 3, 'max': 10, 'text': '3-10 years off', 'emoji': '🟧'},
         1: {'color': 'yellow', 'min': 1, 'max': 2, 'text': '1-2 years off', 'emoji': '🟨'},
         0: {'color': 'green', 'min': 0, 'max': 0, 'text': 'Nailed it!', 'emoji': '🟩'}
         }


def human_to_yr(human_year):
    """Convert year to index (starting at 0) to account for missing year zero between 1 BC and 1 AD."""
    if human_year < 0:
        yr = abs(MIN_HUMAN_YEAR) - abs(human_year)
    else:
        yr = abs(MIN_HUMAN_YEAR) + human_year - 1
    return yr


def yr_to_human(yr):
    """Convert index to human-readable year."""
    if yr < abs(MIN_HUMAN_YEAR):
        human_year = yr - abs(MIN_HUMAN_YEAR)
    else:
        human_year = yr - abs(MIN_HUMAN_YEAR) + 1
    return human_year


class GuessRange:
    def __init__(self, min_yr=float('-inf'), max_yr=float('inf')):
        self.min_yr = min_yr
        self.max_yr = max_yr

    def __and__(self, other):
        if self.min_yr > other.max_yr or other.min_yr > self.max_yr:
            return GuessRange()
        else:
            new_min_yr = max(self.min_yr, other.min_yr)
            new_max_yr = min(self.max_yr, other.max_yr)
            return GuessRange(new_min_yr, new_max_yr)

    def __bool__(self):
        if self.min_yr < 0:
            return False
        else:
            return True

    def __str__(self):
        return f"{yr_to_human(self.min_yr)} ... {yr_to_human(self.max_yr)}"

    def bisect(self):
        return (self.min_yr + self.max_yr) // 2


class YeardleGame:
    def __init__(self):
        self.min_yr = human_to_yr(MIN_HUMAN_YEAR)
        self.max_yr = human_to_yr(datetime.now().year)
        self.guess_ranges = [GuessRange(self.min_yr, self.max_yr)]
        self.guess_count = 0
        self.guesses = []
        self.lastguess = float('-inf')

    def __str__(self):
        r = ', '.join([str(r) for r in self.guess_ranges])
        return f"Ranges: {r if r else None} | Guesses: {self.guess_count} | Last: {yr_to_human(self.lastguess)}"

    def guess(self, guess_yr):
        self.guesses.append(guess_yr)
        self.lastguess = guess_yr
        self.guess_count += 1

    def calc(self, hint):
        up_and_down = []

        down_min = self.lastguess - hints[hint]['min']
        if down_min >= self.min_yr:
            down_max = max(self.min_yr, (self.lastguess - hints[hint]['max']))
            up_and_down.append(GuessRange(down_max, down_min))

        up_min = self.lastguess + hints[hint]['min']
        if up_min <= self.max_yr:
            up_max = min(self.max_yr, (self.lastguess + hints[hint]['max']))
            up_and_down.append(GuessRange(up_min, up_max))

        new_ranges = []
        for old_range in self.guess_ranges:
            for curr_range in up_and_down:
                new_range = old_range & curr_range
                if new_range:
                    new_ranges.append(new_range)

        self.guess_ranges = new_ranges

    def print(self):
        game = [''] * MAX_GUESSES
        for i, yr in enumerate(self.guesses):
            game[i] = str(yr_to_human(yr))
        game[len(self.guesses)] = '_____'
        game = [' '.join(list(string)).rjust(9) for string in game]

        print(f'''
\t╔═════════════╦═════════════╗
\t║  {game[0]}  ║  {game[4]}  ║
\t╠═════════════╬═════════════╣
\t║  {game[1]}  ║  {game[5]}  ║
\t╠═════════════╬═════════════╣
\t║  {game[2]}  ║  {game[6]}  ║
\t╠═════════════╬═════════════╣
\t║  {game[3]}  ║  {game[7]}  ║
\t╚═════════════╩═════════════╝
''')


def input_year(game):
    print("-" * 50)
    print(f"Guess # {game.guess_count+1}")

    game.print()

    if game.guess_count == 0:
        print(f"Allowed range of years: {game.guess_ranges[0]}\n")
    else:
        print("Possible guesses:\n")
        max_r_str_len = 0
        for r in game.guess_ranges:
            if len(str(r)) > max_r_str_len:
                max_r_str_len = len(str(r))
        for r in game.guess_ranges:
            print(f"\t{str(r).rjust(max_r_str_len)} -> Suggested guess: {yr_to_human(r.bisect())}")
        print()

    while True:
        guess = input("Enter your guess: ")
        if guess.replace('-', '', 1).isdecimal():
            guess_yr = human_to_yr(int(guess))
        else:
            print("Not a valid number!\n")
            continue
        if guess_yr >= game.min_yr and guess_yr <= game.max_yr:
            return guess_yr
        else:
            print("Year out of range!\n")


def input_hint():
    print("\nWhat was Yeardle's response to your guess?\n")
    for i, hint in hints.items():
        print(f"\t{i}: {hint['color'].title()}")
    print()

    while True:
        hint = input("Response? ")
        if hint.isdecimal():
            hint = int(hint)
            if hint in hints.keys():
                print(f"-> {hints[hint]['text']}\n")
                return int(hint)
        print("Not a valid answer.\n")


def main():
    game = YeardleGame()

    print("Welcome!\n")

    while True:
        guess_yr = input_year(game)
        game.guess(guess_yr)
        hint = input_hint()
        if hint == 0:
            print(f"Year: {yr_to_human(game.lastguess)}\nGuesses: {game.guess_count}\n")
            input("Enter to quit.")
            break
        if game.guess_count == MAX_GUESSES:
            print("Your guesses are up. Better luck next time!\n")
            input("Enter to quit.")
            break
        game.calc(hint)


if __name__ == "__main__":
    main()
