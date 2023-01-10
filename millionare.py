from questions import questions, answers
from random import randint, shuffle
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
import os


class Questions:
    def __init__(self):
        self._questions = self.create_questions()
        self.answers = self.create_answers()
        self.keys = list(self._questions.keys())
        self.question = None

    @staticmethod
    def create_questions():
        # 'создание словаря 15ти рандомных вопросов'
        game_questions = {}
        availability_check = []

        def generate_recursion():
            def generate_list_of_nums():
                random_num = randint(1, 170)
                if random_num not in availability_check:
                    availability_check.append(random_num)

            if len(availability_check) != 15:
                generate_list_of_nums()
                generate_recursion()

        generate_recursion()

        for i in availability_check:
            game_questions.setdefault(i, questions.get(i))
        return game_questions

    def create_answers(self):
        # 'id вопроса, создание 4 ответов к каждому вопросу один из которых правильный'
        game_answers = {}

        for number_of_question in self._questions:
            answers_list = [answers.get(number_of_question)]
            while len(answers_list) != 4:
                answers_list.append(answers.get(randint(1, 170)))
            shuffle(answers_list)
            game_answers.setdefault(number_of_question, answers_list)
        return game_answers

    def take_question(self):
        return self._questions[self.keys[0]]

    def take_answer(self):
        return self.answers[self.keys[0]]

    def check_answer(self, player_answer):
        if player_answer == answers.get(self.keys[0]):
            return True
        else:
            return False

    def next_question(self):
        del self.keys[0]


class Game:
    def __init__(self):
        self.que = Questions()
        self.varriants = ['a', 'b', 'c', 'd']
        self.total = 0

    def check_correct_answer(self):
        player_answer = input('>')
        if player_answer in self.varriants:
            if self.que.check_answer(self.que.take_answer()[self.varriants.index(player_answer)]):
                self.total += 1
            self.que.next_question()
        else:
            print('Некорректно указан ответ, попробуйте еще раз...')
            self.check_correct_answer()

    def start_game(self):
        for _ in range(15):
            print(f'\n{self.que.take_question()}')
            for a, b in zip(self.varriants, self.que.take_answer()):
                print(a, b)
            self.check_correct_answer()
        print(f'Викторина окончена, Ваш результат: {self.total} из 15 правильных ответов.')


def menu():
    bot = Bot(token=os.getenv('TOKEN'))
    dp = Dispatcher(bot)
    photo = open('images/main.png', 'rb')
    help_text = " Приветствую тебя в бета тестированни игры как стать миллионером. По скольку проект маленький " \
                "детали игры могут отличаться от оригинала, оставь свой коментарий на гите, я постараюсь в ближайшее " \
                "время выпустить обновление.\n На данном етапе имееться рандомный выбор ответов из правильных.\n" \
                " В скоре будет добавлена позможность выбора помощи зала, друга и 50/50, так же вместо тотала " \
                "правильных ответов, будет отображаться сумма выйграша.\n\n"
    keyboard = ReplyKeyboardMarkup()
    button_new = KeyboardButton('Новая игра')
    keyboard.add(button_new)

    @dp.message_handler(commands=['start', 'help'])
    async def command_start(message: types.Message):
        await message.reply('ok', reply_markup=keyboard)
        await bot.send_photo(message.from_user.id, photo)
        await bot.send_message(message.from_user.id, help_text)

    @dp.message_handler()
    async def new_game(message: types.Message):
        if message.text.lower() == 'новая игра':
            await message.reply('создаю игру', reply_markup=keyboard.add(KeyboardButton('hihi')))

    executor.start_polling(dp, skip_updates=True)

    # request1 = input('>')
    # if request1.lower() == 'new':
    #     print('\n И так, для тебя подготовили 15 вопросов твоя задача дать как можно больше правильных ответов.\n '
    #           'для продолжения нажми Enter<-')
    #     input()
    #     g = Game()
    #     g.start_game()
    # elif request1.lower() == 'q':
    #     pass
    # else:
    #     menu()


if __name__ == '__main__':
    menu()
