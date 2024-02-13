# вопросы и варианты ответов
content_for_quiz = {"first_question": ["Когда вы родились?", ["Летом", "Осенью", "Весной", "Зимой"]],
                    "second_question": ["Какую пищу вы употребляете?",
                                        ["Я ем ВСЁ!", "Не ем мясо", "Отдаю предпочтение мясным блюдам"]],
                    "third_question": ["Как вы переносите летний зной?",
                                       ["При первой же возможности прячусь в тень", "Жара мне нипочём"]],
                    "fourth_question": ["А плавать умеете?",
                                        ["Плаваю без круга!", "Могу помочить ноги на берегу", "Я не умею плавать"]],
                    "fifth_question": ["Важно ли для вас общение с окружающими?",
                                       ["Конечно, без него никак", "Я волк-одиночка"]]
                    }

# словарь для перевода ответов юзера для дальнейшего сравнения с характеристиками животных
transform_answers = {"Летом": ["Лето"],
                     "Осенью": ["Осень"],
                     "Зимой": ["Зима"],
                     "Весной": ["Весна"],
                     "Я ем ВСЁ!": ["Растения", "Мясо"],
                     "Не ем мясо": ["Растения"],
                     "Отдаю предпочтение мясным блюдам": ["Мясо"],
                     "При первой же возможности прячусь в тень": ["Лес"],
                     "Жара мне нипочём": ["Саванна"],
                     "Плаваю без круга!": ["Плавает"],
                     "Могу помочить ноги на берегу": ["Не любит"],
                     "Я не умею плавать": ["Не умеет"],
                     "Конечно, без него никак": ["Стадное"],
                     "Я волк-одиночка": ["Одиночка"]
                     }


# класс животных с фиксированным набором характеристик
class Animals:
    def __init__(self, animal, birth, eat, temp, swim, social):
        self.animal = animal
        self.birth = birth
        self.eat = eat
        self.area = temp
        self.swim = swim
        self.social = social


# животные с заданными хар-ками. Реализация ч-з списки, т.к. у некоторых мб по 2 варианта хар-к
lion = Animals(["Лев"], ["Лето"], ["Мясо"], ["Саванна"], ["Не любит"], ["Стадное"])
bear = Animals(["Медведь"], ["Зима", "Весна"], ["Растения", "Мясо"], ["Лес"], ["Плавает"], ["Одиночка"])
giraffe = Animals(["Жираф"], ["Лето", "Осень"], ["Растения"], ["Саванна"], ["Не умеет"], ["Стадное"])
orangutan = Animals(["Орангутан"], ["Весна"], ["Растения"], ["Лес"], ["Не умеет"], ["Стадное"])
crocodile = Animals(["Крокодил"], ["Лето", "Осень"], ["Мясо"], ["Саванна"], ["Плавает"], ["Одиночка"])

# словарь с животными для дальнейшего сопоставления ответов юзера с характеристиками животных
animals = {"Лев": lion, "Медведь": bear, "Жираф": giraffe, "Орангутан": orangutan, "Крокодил": crocodile}


class Result:
    def __init__(self, answer_from_user, user):
        self.answer_from_user = answer_from_user
        self.system_answers = transform_answers
        self.user = user
        self.animal_result = {}
        self.processed_answers = []
        self.user_result = {}

    def transformation(self):  # преобразование ответов юзера в шаблонный вид
        for answer in self.answer_from_user:
            new_value = self.system_answers[answer]
            self.processed_answers.append(new_value)
            print(self.processed_answers)
        return self.processed_answers

    def result(self):  # подсчет кол-ва совпавших характеристик для каждого животного
        for key, value in animals.items():
            count = 0
            for birth in self.processed_answers[0]:
                if birth in value.birth:
                    count += 1
                    break
            for eat in self.processed_answers[1]:
                if eat in value.eat:
                    count += 1
                    break
            for area in self.processed_answers[2]:
                if area in value.area:
                    count += 1
                    break
            for swim in self.processed_answers[3]:
                if swim in value.swim:
                    count += 1
            for social in self.processed_answers[4]:
                if social in value.social:
                    count += 1
            self.animal_result[key] = count
            print(self.animal_result)

    def get_animal_result(self):  # определение животного с наибольшим кол-вом совпадений с ответами юзера
        max_value = 0
        for key, value in self.animal_result.items():
            if value > max_value:
                max_value = value
                self.user_result[self.user] = [key, f"{round((int(max_value) / len(self.answer_from_user)) * 100, 2)}%"]
        return self.user_result


def get_result(usr_answ, user):  # преобразование ответов юзера в итоговый результат с помощью методов Result
    results = Result(usr_answ, user)
    results.transformation()
    results.result()
    what_animal = results.get_animal_result()
    percents = 0
    totem_animal = ""
    for key, value in what_animal.items():
        totem_animal = value[0]
        percents = value[1]
    text = f"Подумать только, вы на целых {percents} {totem_animal.lower()}!"
    return [text, what_animal]
