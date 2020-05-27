class Track:
    def __init__(self):
        # Store the number of success
        # in one round of quiz
        self.score = 0
        # List of word the Player
        # couldn't answer correctly
        self.fails = []
        # Store the number of question
        # the Player answered for one round
        self.num_of_question = 0
        # Track the 10 last questioned words in order to avoid
        # the same word being questioned twice in short time
        self.last_questioned = []

    def update(self, question, score_up=1, fail=None):
        """ Handle the tracking for every question"""
        self.num_of_question += 1
        if fail:
            self.fails.append(fail)
            return
        self.score += score_up
        self.last_questioned.append(question)
        if len(self.last_questioned) > 15:
            self.last_questioned.remove(self.last_questioned[0])

    def get_average_success(self):
        return round(self.score / self.num_of_question, 3) if self.num_of_question > 0 else 0
