from telebot.async_telebot import AsyncTeleBot
from telebot import types
from config import TOKEN
from sendmail import send_email
from bot_content import content_for_quiz, get_result
import asyncio
import aiohttp

zoo_bot = AsyncTeleBot(TOKEN)

user_state = {}  # словарь для хранения текущего стейта пользователя, методы обновления и получения стейтов ниже


def set_user_state(user_id, state):
    user_state[user_id] = state


def get_user_state(user_id):
    return user_state.get(user_id, None)


user_answers = {}  # словарь для хранения всех ответов пользователя


def add_user_answer(user_id, answer):
    user_answers[user_id].append(answer)


def get_user_answers(user_id):
    return user_answers.get(user_id)


final_result = {}  # словарь для хранения итогового результата пользователя в формате user_id: [животное,


# процент совпадения]


def set_user_final_result(result_for_save):
    final_result.update(result_for_save)


def get_user_final_result(user_id):
    return final_result.get(user_id)


user_feedbacks = {}  # словарь для хранения отзывов пользователей


def add_feedback(username, feedback):
    if username not in user_feedbacks:
        user_feedbacks[username] = list()
    user_feedbacks[username].append(feedback)


class SomethingGoesWrongException(Exception):
    pass


class Questions:  # забираем текст вопроса и варианты ответов из content_for_quiz
    def __init__(self, number):
        self.number = number
        self.text = content_for_quiz[self.number][0]
        self.answers = content_for_quiz[self.number][1]


class Pages:  # класс готовых страниц для отправки из текста и списка кнопок
    def __init__(self, text, names):  # Названия кнопок передавать списком, даже если она одна
        self.text = text
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        self.names = names
        for name in self.names:
            self.name = name
            button = types.KeyboardButton(self.name)
            keyboard.add(button)
            self.keyboard = keyboard

    async def get_page(self, message):  # отправка страницы
        await zoo_bot.send_message(message.chat.id, self.text, reply_markup=self.keyboard)

    async def get_page_with_image(self, message, image):  # отправка страницы с картинкой
        await zoo_bot.send_photo(message.chat.id, photo=open("images/" + image, "rb"), caption=self.text,
                                 reply_markup=self.keyboard)

    async def get_page_with_gif(self, message, image):  # отправка страницы с гифкой
        await zoo_bot.send_animation(message.chat.id, animation=open("images/" + image, "rb"), caption=self.text,
                                     reply_markup=self.keyboard)


# создание объектов-вопросов из content_for_quiz
first_question = Questions("first_question")
second_question = Questions('second_question')
third_question = Questions('third_question')
fourth_question = Questions('fourth_question')
fifth_question = Questions('fifth_question')

# создание готовых страниц для отправки (текст+клавиатура)
first_question_state = Pages(first_question.text, first_question.answers)
second_question_state = Pages(second_question.text, second_question.answers)
third_question_state = Pages(third_question.text, third_question.answers)
fourth_question_state = Pages(fourth_question.text, fourth_question.answers)
fifth_question_state = Pages(fifth_question.text, fifth_question.answers)
start_quiz = Pages("Пройдите тест и выясните, много ли общего у вас и обитателей нашего зоопарка.\n"
                   "Приступим?", ["Погнали", "Главное меню"])
main_menu = Pages("Бот к вашим услугам.", ["Пройти тест", "Поддержка", "Оставить отзыв"])
start_command = Pages("Приветствуем вас в нашем боте.\nЗдесь вы можете пройти тест на поиск общих черт с обитателями "
                      "московского зоопарка", ["Пройти тест", "Поддержка", "Оставить отзыв"])
take_feedback = Pages("Здесь вы можете оставить свой отзыв о викторине и работе нашего бота.\n"
                      "Напишите свое мнение и отправьте его.", ["Главное меню"])
share_result = Pages("Вы можете рассказать о своих результатах, переслав сообщение выше или отправив скопированный "
                     "текст.", ["Главное меню"])
send_feedback = Pages("Спасибо за отзыв!", ["Главное меню"])
quiz_end = Pages("Потрясающее совпадение.\n"
                 "\nСчитаете, что это действительно про вас? Или отдадите предпочтение другому животному? "
                 "Это не важно, ведь если вы любите животных, и их судьбы вам небезразличны, то благодаря программе "
                 "опеки вы можете стать их опекуном!\n"
                 "\nСтав одним из участников нашей программы опеки, вы получите право бесплатного посещения зоопарка, "
                 "фотографии ваших подопечных в подарок, а также – особое место на сайте нашего зоопарка.",
                 ["Поделиться результатом", "Попробовать еще раз", "Главное меню"])
helper = Pages("В этом боте вы можете узнать, сколько общего у вас обитателями московского зоопарка", ["Главное меню"])
connect_with_support = Pages("Отправьте ваш вопрос нашей поддержке. Мы самостоятельно свяжемся с вами.",
                             ["Главное меню"])

# словарь со стейтами, значения - готовый контент для отправки(текст сообщения, клавиатура)
states = {"main_menu": main_menu,
          "start_quiz": start_quiz,
          "first_question_state": first_question_state,
          "second_question_state": second_question_state,
          "third_question_state": third_question_state,
          "fourth_question_state": fourth_question_state,
          "fifth_question_state": fifth_question_state,
          "quiz_end": quiz_end,
          "share_result": share_result,
          "help": helper,
          "take_feedback": take_feedback,
          "send_feedback": send_feedback,
          "connect_with_support": connect_with_support
          }


@zoo_bot.message_handler(commands=['start'])
async def start_message(message: types.Message):
    user_id = message.from_user.id
    await start_command.get_page_with_image(message, "start_image.jpg")
    set_user_state(user_id, "main_menu")


@zoo_bot.message_handler(commands=['help'])
async def help_message(message: types.Message):
    await helper.get_page(message)


# Валидация любого введенного в бота текста (кроме команд), с  установкой нужного стейта, если нажата одна из кнопок
# сценария. Здесь реализована логика перехода к нужному стейту
@zoo_bot.message_handler(func=lambda message: True)
async def handle_quiz(message):
    user_id = message.from_user.id
    username = message.from_user.username
    current_state = get_user_state(user_id)
    try:
        if current_state is None or message.text == "Главное меню":
            await main_menu.get_page(message)
            set_user_state(user_id, "main_menu")
            # current_state = "main_menu"
        elif message.text == "Поддержка" and current_state == "main_menu":
            await connect_with_support.get_page(message)
            set_user_state(user_id, "connect_with_support")
        elif message.text and current_state == "connect_with_support":
            if get_user_final_result(user_id) is None:
                result = "Тест еще не пройден"
            else:
                result = f"{get_user_final_result(user_id)[0]} на {get_user_final_result(user_id)[1]}"
            await zoo_bot.send_message(message.chat.id, text="Отправляю сообщение, подождите, пожалуйста.")
            send_email(username, message.text, result)
            await zoo_bot.send_message(message.chat.id, text="Ваше сообщение доставлено. Наш менеджер скоро "
                                                             "свяжется с вами.")
            await main_menu.get_page(message)
            set_user_state(user_id, "main_menu")
        elif message.text == "Оставить отзыв" and current_state == "main_menu":
            await take_feedback.get_page(message)
            set_user_state(user_id, "take_feedback")
        elif message.text and current_state == "take_feedback":
            add_feedback(username, message.text)
            await send_feedback.get_page(message)
            set_user_state(user_id, "send_feedback")
        elif message.text == "Пройти тест" and current_state == "main_menu":
            await start_quiz.get_page(message)
            set_user_state(user_id, "start_quiz")
        elif (
                message.text == "Погнали" and current_state == "start_quiz") or message.text == "Попробовать еще раз" and current_state == "quiz_end":
            user_answers[user_id] = []
            final_result[user_id] = []
            set_user_state(user_id, "first_question_state")
            current_state = get_user_state(user_id)
            await handle_quiz_steps(message, current_state, "first_question_image.gif")
        elif message.text in first_question_state.names and current_state == "first_question_state":
            add_user_answer(user_id, message.text)
            set_user_state(user_id, "second_question_state")
            current_state = get_user_state(user_id)
            await handle_quiz_steps(message, current_state, "second_question_image.gif")
        elif message.text in second_question_state.names and current_state == "second_question_state":
            add_user_answer(user_id, message.text)
            set_user_state(user_id, "third_question_state")
            current_state = get_user_state(user_id)
            await handle_quiz_steps(message, current_state, "third_question_image.gif")
        elif message.text in third_question_state.names and current_state == "third_question_state":
            add_user_answer(user_id, message.text)
            set_user_state(user_id, "fourth_question_state")
            current_state = get_user_state(user_id)
            await handle_quiz_steps(message, current_state, "fourth_question_image.gif")
        elif message.text in fourth_question_state.names and current_state == "fourth_question_state":
            add_user_answer(user_id, message.text)
            set_user_state(user_id, "fifth_question_state")
            current_state = get_user_state(user_id)
            await handle_quiz_steps(message, current_state, "fifth_question_image.gif")
        elif message.text in fifth_question_state.names and current_state == "fifth_question_state":
            set_user_state(user_id, "quiz_end")
            add_user_answer(user_id, message.text)
            text_result = get_result(get_user_answers(user_id), user_id)[0]
            result_for_save = get_result(get_user_answers(user_id), user_id)[1]
            set_user_final_result(result_for_save)
            animal = get_user_final_result(user_id)[0]
            photo = open("images/" + animal + ".jpg", "rb")
            link = "[сайте](https://moscowzoo.ru/my-zoo/become-a-guardian/)"
            go_to_site = f"Узнать подробнее о программе опеки вы можете на нашем {link}."
            await zoo_bot.send_photo(message.chat.id, photo=photo, caption=text_result)
            await quiz_end.get_page(message)
            await zoo_bot.send_message(message.chat.id, go_to_site, parse_mode='Markdown')
        elif message.text == "Поделиться результатом" and current_state == "quiz_end":
            set_user_state(user_id, "share_result")
            animal = get_user_final_result(user_id)[0]
            link = "[Zoo quiz](https://t.me/zoo_quiz_bot)"
            text_for_friend = f"{animal} - вот мое тотемное животное!\n" \
                              f"В боте {link} ты можешь узнать, с каким из животных у тебя много общего. "
            await zoo_bot.send_message(message.chat.id, text_for_friend, parse_mode='Markdown')
            await share_result.get_page(message)
        else:
            keyboard = states[current_state].keyboard
            await zoo_bot.send_message(message.chat.id, "Извините, я вас не понимаю.\nНажмите на одну из кнопок меню",
                                       reply_markup=keyboard)
    except SomethingGoesWrongException as e:
        await zoo_bot.send_message(message.chat.id, "Кажется, что-то пошло не так...\n"
                                                    "Попробуйте начать заново /start")


# печать того page, который соответствует state из словаря states
async def handle_quiz_steps(message, state, image):
    current_state = states.get(state)
    await current_state.get_page_with_gif(message, image)


asyncio.run(zoo_bot.polling())
