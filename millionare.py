from questions import questions, answers
from random import randint, shuffle
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
import os
import asyncio


bot = Bot(token=os.getenv('TOKEN'))
dp = Dispatcher(bot)
photo = open('images/main.png', 'rb')
help_text = " Приветствую тебя в бета тестированни игры как стать миллионером. По скольку проект маленький " \
            "детали игры могут отличаться от оригинала, оставь свой коментарий на гите, я постараюсь в ближайшее " \
            "время выпустить обновление.\n На данном етапе имееться рандомный выбор ответов из правильных.\n" \
            " В скоре будет добавлена позможность выбора помощи зала, друга и 50/50.\n\n"
button_new = InlineKeyboardButton('Новая игра', callback_data='button_new')
keyboard_start = InlineKeyboardMarkup().add(button_new)
button1 = InlineKeyboardButton('Продолжить', callback_data='continue_start')
button3 = InlineKeyboardButton('Продолжить', callback_data='continue')
button4 = KeyboardButton('/start')
kb1 = InlineKeyboardMarkup().add(button1)
kb3 = InlineKeyboardMarkup().add(button3)
kb4 = ReplyKeyboardMarkup().add(button4)


class Questions:
    def __init__(self):
        self._questions = self.create_questions()
        self.answers = self.create_answers()
        self.keys = list(self._questions.keys())

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

    def take_answers(self):
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
        self.money = ['0', '100', '200', '300', '500', '1k', '2k', '4k', '8k', '16k', '32k', '64k', '125k', '250k', '500k',
                      '1000k']
        self.__game_flag = False

    def check_correct_answer(self, player_answer):
        if self.que.check_answer(self.que.take_answers()[self.varriants.index(player_answer)]):
            self.total += 1
            self.que.next_question()
        else:
            self.__game_flag = True

    async def send_question(self, user_id):
        kb2 = InlineKeyboardMarkup()
        for a, b, i in zip(self.varriants, self.que.take_answers(), [1, 2, 3, 4]):
            button2 = InlineKeyboardButton(a + '. ' + b, callback_data=a)
            if i % 2 == 1:
                kb2.add(button2)
            else:
                kb2.row(button2)
        await bot.send_message(user_id, self.que.take_question(), reply_markup=kb2)

    async def send_msg_after_check(self, user_id):
        if self.__game_flag:
            if self.total >= 5:
                await bot.send_message(user_id, f'Не в этот раз, но Вы уходите не с пустыми руками, у вас есть незгораемая '
                                          f'сумма {self.money[self.total-self.total%5]} UAH.',
                                          reply_markup=kb3)
            else:
                await bot.send_message(user_id, 'К моему сожелению Вы проиграли =_(',
                                          reply_markup=keyboard_start)
        else:
            if self.total >= 5:
                await bot.send_message(user_id, f'Вы выиграли {self.money[self.total]} UAH. У Вас есть незгораемая '
                                          f'сумма {self.money[self.total-self.total%5]} UAH. Хотите продолжить?',
                                          reply_markup=kb3)
            else:
                await bot.send_message(user_id, f'Вы выиграли {self.money[self.total]} UAH. Хотите продолжить?',
                                          reply_markup=kb3)


def menu():
    @dp.message_handler(commands=['start', 'help'])
    async def command_start(message: types.Message):
        await bot.send_photo(message.from_user.id, photo)
        await bot.send_message(message.from_user.id, help_text, reply_markup=keyboard_start)

    @dp.callback_query_handler(lambda c: c.data == 'button_new')
    async def callback_kb_main_pre_new(callback_query: types.CallbackQuery):
        await bot.send_message(callback_query.from_user.id,
                               'И так, для тебя подготовили 15 вопросов твоя задача дать как можно больше правильных '
                               'ответов.\n Для продолжения нажми "Продолжить"',
                               reply_markup=kb1)

    @dp.callback_query_handler(lambda c: c.data == 'continue_start')
    async def callback_kb_main_new_game(callback_query: types.CallbackQuery):
        global g
        g = Game()
        asyncio.create_task(g.send_question(callback_query.from_user.id))

    @dp.callback_query_handler(lambda c: c.data in ['a', 'b', 'c', 'd'])
    async def callback_kb_game_answer(callback_query: types.CallbackQuery):
        g.check_correct_answer(callback_query.data)
        asyncio.create_task(g.send_msg_after_check(callback_query.from_user.id))

    @dp.callback_query_handler(lambda c: c.data in ['continue'])
    async def callback_kb_continue(callback_query: types.CallbackQuery):
        asyncio.create_task(g.send_question(callback_query.from_user.id))

    executor.start_polling(dp, skip_updates=True)


if __name__ == '__main__':
    menu()
