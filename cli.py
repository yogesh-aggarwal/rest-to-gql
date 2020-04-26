from __future__ import print_function, unicode_literals
from PyInquirer import prompt, print_json
from colorama import init


init()

questions = [
    {
        'type': 'input',
        'name': 'first_name',
        'message': 'What\'s your first name',
    }
]

answers = prompt(questions)
print_json(answers)  # use the answers as input for your app