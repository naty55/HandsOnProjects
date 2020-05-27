import json


class DictWords:
    def __init__(self):
        self.dic_file = './dict.json'
        self.arr_file = './words.txt'
        self.words = self.get_words()
        self.recent_words = self.get_rwords_from_file()
        self.new_words = []

    def get_recent_words(self):
        """ Return a dict with 10 recent words and their translation """

        recent_dict = {}
        for item in self.recent_words:
            recent_dict[item] = self.words.get(item, 'Not Found!')
        return recent_dict

    def get_rwords_from_file(self):
        with open(self.arr_file, 'r') as f:
            return list(map(lambda x: x, f.read().strip(',').split(',')))

    def get_words(self):
        with open(self.dic_file, 'rb') as f:
            return json.load(f)

    def save_words(self):
        with open(self.arr_file, 'w') as f:
            f.write(','.join(self.recent_words).strip(','))
        with open(self.dic_file, 'w') as f:
            json.dump(self.words, f, indent=2)

    def print(self):
        print(self.words)
        print(self.recent_words)

    def add_entry(self, entry):
        """ Add an entry to the dict and then save it"""
        self.words.update(entry)
        for word in entry.keys():
            if word not in self.recent_words:
                print(word, 'Added')
                self.recent_words.append(word)
            if len(self.recent_words) > 10:
                self.recent_words.remove(self.recent_words[0])
        self.save_words()

    def get_dict(self):
        return self.words

dict_words = DictWords()
# dict_words.print()
