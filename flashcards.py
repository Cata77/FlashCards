import json
import os
import argparse
from io import StringIO

cards = dict()
parser = argparse.ArgumentParser()
parser.add_argument('-i', '--import_from', action="store")
parser.add_argument('-e', '--export_to', action="store")
args = parser.parse_args()


def log_output(message):
    print(message)
    in_memory_file.write(message+'\n')


def check_term_already_exists(term):
    return next((term for key in cards if key == term), None)


def check_definition_already_exists(definition):
    return next((definition for key in cards if cards[key]['definition'] == definition), None)


def check_if_definition_match_for_another_term(definition):
    return next((key for key in cards if cards[key]['definition'] == definition), None)


def check_wrong_answer(answer, definition):
    term = check_if_definition_match_for_another_term(answer)
    if term is None:
        log_output(f'Wrong. The right answer is "{definition}".')
    else:
        log_output(f'Wrong. The right answer is "{definition}", but your definition is correct for "{term}".')


def add_flashcard():
    log_output(f'The card:')
    term = input()
    in_memory_file.write(term+'\n')
    while check_term_already_exists(term) is not None:
        log_output(f'The term "{term}" already exists. Try again:')
        term = input()
        in_memory_file.write(term + '\n')

    log_output(f'The definition of the card:')
    definition = input()
    in_memory_file.write(definition + '\n')
    while check_definition_already_exists(definition) is not None:
        log_output(f'The definition "{definition}" already exists. Try again:')
        definition = input()
        in_memory_file.write(definition + '\n')

    cards[term] = dict()
    cards[term]['definition'] = definition
    cards[term]['mistakes'] = 0
    log_output(f'The pair ("{term}":"{definition}") has been added.\n')


def remove_flashcard():
    log_output('Which card?')
    card = input()
    in_memory_file.write(card)
    if card in cards:
        cards.pop(card)
        log_output('The card has been removed.\n')
    else:
        log_output(f'Can\'t remove "{card}": there is no such card.\n')


def import_file():
    log_output('File name')
    if args.import_from:
        file_name = args.import_from
    else:
        file_name = input()
    in_memory_file.write(file_name + '\n')
    if os.path.isfile(f'{os.getcwd()}/{file_name}'):
        with open(file_name, 'r') as file:
            imported_dict = json.loads(file.read())
            cards.update(imported_dict)
        log_output(f'{len(imported_dict)} cards have been loaded.\n')
    else:
        log_output('File not found.\n')


def export_file():
    log_output('File name')
    if args.export_to:
        file_name = args.export_to
    else:
        file_name = input()
    in_memory_file.write(file_name + '\n')
    with open(file_name, 'w') as file:
        file.write(json.dumps(cards, indent=4))
    log_output(f'{len(cards)} cards have been saved.\n')


def ask_user():
    log_output('How many times to ask?')
    times_to_ask = int(input())
    in_memory_file.write(str(times_to_ask) + '\n')

    i = 1
    while i <= times_to_ask:
        for key, value in cards.items():
            if i > times_to_ask:
                return main()

            log_output(f'Print the definition of "{key}":')
            answer = input()
            in_memory_file.write(answer + '\n')
            if answer == value:
                log_output('Correct!\n')
            else:
                check_wrong_answer(answer, value)
                cards[key]['mistakes'] += 1
            i += 1


def log_file():
    log_output('File name')
    file_name = input()
    in_memory_file.write(file_name + '\n')
    log_output('The log has been saved.\n')
    in_memory_file.seek(0)
    with open(file_name, 'w') as file:
        for line in in_memory_file:
            file.write(line)


def hardest_card():
    if len(cards):
        max_mistake = max(cards.values(), key=lambda x: x["mistakes"])["mistakes"]
        if max_mistake == 0:
            log_output('There are no cards with errors\n')
            return main()
        most_mistakes_card = [card for card in cards if cards[card]["mistakes"] == max_mistake]
        if len(most_mistakes_card) > 1:
            log_output(f'The hardest cards are {", ".join(f"{card}" for card in most_mistakes_card)}. '
                       f'You have {max_mistake} errors answering them.\n')
        else:
            log_output(f'The hardest card is "{most_mistakes_card[0]}". You have {max_mistake} errors answering it.\n')
    else:
        log_output('There are no cards with errors.\n')


def reset_stats():
    for card in cards:
        cards[card]['mistakes'] = 0
    log_output('Card statistics have been reset.\n')


def main():
    actions = {
        'add': add_flashcard,
        'remove': remove_flashcard,
        'import': import_file,
        'export': export_file,
        'ask': ask_user,
        'log': log_file,
        'hardest card': hardest_card,
        'reset stats': reset_stats
    }

    if args.import_from:
        import_file()
    while True:
        log_output('Input the action (add, remove, import, export, ask, exit, log, hardest card, reset stats):')
        command = input()
        in_memory_file.write(command + '\n')

        if command == 'exit':
            log_output('Bye bye!')
            if args.export_to:
                export_file()
            in_memory_file.close()
            exit()

        action = actions.get(command)
        if action:
            action()


if __name__ == '__main__':
    in_memory_file = StringIO()
    main()
