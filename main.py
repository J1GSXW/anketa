import asyncio
import logging
import os
from datetime import datetime, date

import gspread
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher.filters.state import State
from aiogram.dispatcher.filters.state import StatesGroup
from aiogram.types import BotCommand, BotCommandScopeDefault
from aiogram.types import CallbackQuery
from aiogram.types import InlineKeyboardButton
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import ReplyKeyboardRemove
from aiogram.utils import executor
from aiogram_datepicker import Datepicker, DatepickerSettings, DatepickerCustomAction

# from background import keep_alive

logging.basicConfig(level=logging.INFO)

TOKEN = '6285611257:AAGcsm_qWuJKPJsWlpdTX9kGiyKKDOU5DS4'
CHAT_ID = '-1001609605973'

bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

credentials_path = 'anketa-395005-329ea72fdec7.json'
spreadsheet_id = '1Q8oZ65ZuZkfmmax99DF9YInRO3zxt7ZFYyM112Pk7JY'

gc = gspread.service_account(filename='anketa-395005-329ea72fdec7.json')
sht1 = gc.open_by_key('1Q8oZ65ZuZkfmmax99DF9YInRO3zxt7ZFYyM112Pk7JY')
worksheet = sht1.worksheet("Анкеты из бота")
worksheet2 = sht1.worksheet("Анкеты из бота(незавершенные)")


class Form(StatesGroup):
    name = State()
    birth_date = State()
    phone_number = State()
    social_links = State()
    education_status = State()
    education_details = State()
    is_our_guest = State()
    user_link = State()
    job_preferences = State()
    last_job = State()
    dismissal_reason = State()
    why_us = State()
    main_dream = State()
    favorite_drink = State()
    new_acquaintances = State()
    emotions = State()
    work_schedule = State()
    last_job_recommendation = State()
    know_vacancy = State()
    if_you_small = State()
    remark = State()
    what_closely = State()
    freeze_pinguin = State()
    theft = State()
    two_employers = State()


LAST_PROCESSED_ROW_FILE = "last_row.txt"
LAST_PROCESSED_ROW_FILE_2 = "last_row2.txt"


def get_last_processed_row(filename):
    if os.path.exists(filename):
        with open(filename, "r") as file:
            return int(file.read())
    return 1  # Если файл не существует, начни с первой строки


def update_last_processed_row(row, filename):
    with open(filename, "w") as file:
        file.write(str(row))


user_commands = [
    BotCommand("start", "Начать анкету"),
    BotCommand("stop", "Остановить\перезапустить анкету")
]


def _get_datepicker_settings():
    class CancelAction(DatepickerCustomAction):
        action: str = 'cancel'
        label: str = 'Отменить'

        def get_action(self, view: str, year: int, month: int, day: int) -> InlineKeyboardButton:
            return InlineKeyboardButton(self.label,
                                        callback_data=self._get_callback(view, self.action, year, month, day))

        async def process(self, query: CallbackQuery, view: str, _date: date) -> bool:
            if view == 'day':
                await query.message.delete()
                return False

    return DatepickerSettings(
        initial_view='year',
        initial_date=datetime.now().date(),
        views={
            'day': {
                'show_weekdays': False,
                'weekdays_labels': ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'],
                'header': ['prev-year', 'days-title', 'next-year'],
                'footer': ['prev-month', 'ignore', 'next-month', ['cancel']],
            },
            'month': {
                'months_labels': ['Янв', 'Фев', 'Март', 'Апр', 'Май', 'Июнь', 'Июль', 'Авг', 'Сен', 'Окт', 'Нояб',
                                  'Дек'],
                'header': ['prev-year', 'year', 'next-year'],
                'footer': []
            },
            'year': {
                'header': [],
                'footer': ['prev-years', 'next-years']
            }
        },
        labels={
            'prev-year': '<<',
            'next-year': '>>',
            'prev-years': '<<',
            'next-years': '>>',
            'days-title': '{month} {year}',
            'selected-day': '{day} *',
            'selected-month': '{month} *',
            'present-day': '• {day} •',
            'prev-month': '<',
            'select': 'Select',
            'next-month': '>',
            'ignore': '⠀'
        },
        custom_actions=[CancelAction]
    )


async def set_commands(dp: Dispatcher):
    await dp.bot.set_my_commands(user_commands, scope=BotCommandScopeDefault())


async def name_input_timeout(state: FSMContext, message: types.Message):
    await asyncio.sleep(3600)
    async with state.proxy() as data:
        today = date.today()
        timestamp = today.strftime("%m/%d/%Y")
        last_row = get_last_processed_row(LAST_PROCESSED_ROW_FILE_2)
        name = data.get('name')
        birhdate = data.get('birth_date')
        phone_number = data.get('phone_number')
        social_links = data.get('social_links')
        education_status = data.get('education_status')
        education_details = data.get('education_details')
        is_our_guest = data.get('is_our_guest')
        job_preferences = data.get('job_preferences')
        last_job = data.get('last_job')
        dismissal_reason = data.get('dismissal_reason')
        why_us = data.get('why_us')
        main_dream = data.get('main_dream')
        favorite_drink = data.get('favorite_drink')
        new_acquaintances = data.get('new_acquaintances')
        emotions = data.get('emotions')
        work_schedule = data.get('work_schedule')
        last_job_recommendation = data.get('last_job_recommendation')
        know_vacancy = data.get('know_vacancy')
        if_you_small = data.get('if_you_small')
        remark = data.get('remark')
        what_closely = data.get('what_closely')
        freeze_pinguin = data.get('freeze_pinguin')
        theft = data.get('theft')
        two_employers = data.get('two_employers')

        worksheet2.update(f"A{last_row}", str(timestamp))
        worksheet2.update(f"B{last_row}", name)
        worksheet2.update(f"C{last_row}", birhdate)
        worksheet2.update(f"D{last_row}", phone_number)
        worksheet2.update(f"E{last_row}", social_links)
        worksheet2.update(f"F{last_row}", education_status)
        worksheet2.update(f"G{last_row}", education_details)
        worksheet2.update(f"H{last_row}", is_our_guest)
        worksheet2.update(f"I{last_row}", job_preferences)
        worksheet2.update(f"J{last_row}", last_job)
        worksheet2.update(f"K{last_row}", dismissal_reason)
        worksheet2.update(f"L{last_row}", why_us)
        worksheet2.update(f"M{last_row}", main_dream)
        worksheet2.update(f"N{last_row}", favorite_drink)
        worksheet2.update(f"O{last_row}", new_acquaintances)
        worksheet2.update(f"P{last_row}", emotions)
        worksheet2.update(f"Q{last_row}", work_schedule)
        worksheet2.update(f"R{last_row}", last_job_recommendation)
        worksheet2.update(f"S{last_row}", know_vacancy)
        worksheet2.update(f"T{last_row}", if_you_small)
        worksheet2.update(f"U{last_row}", remark)
        worksheet2.update(f"V{last_row}", what_closely)
        worksheet2.update(f"W{last_row}", freeze_pinguin)
        worksheet2.update(f"X{last_row}", theft)
        worksheet2.update(f"Y{last_row}", two_employers)

    last_row += 1
    update_last_processed_row(last_row, LAST_PROCESSED_ROW_FILE_2)
    await state.finish()
    await message.answer("К сожалению время вышло, ты можешь начать анкету заново командой /start")


async def create_task(state: FSMContext, message: types.Message):
    async with state.proxy() as data:
        user_id = message.from_user.id
        if user_id in user_timers:
            user_timers[user_id].cancel()

        task = asyncio.create_task(name_input_timeout(state, message))
        user_timers[user_id] = task


user_timers = {}


@dp.message_handler(Command('start'))
async def start_cmd_handler(message: types.Message, state: FSMContext):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(KeyboardButton("Начать"))
    await state.reset_state()
    await message.reply(
        "Привет, это анкета в Coffee Like KMS. Чтобы попасть в нашу команду, тебе нужно максимально подробно и"
        " честно ответить на все вопросы и выполнить задания. Прояви смекалку!\n"
        "Обрати внимание, на прохождение анкеты у тебя будет 1 час, после чего она автоматически"
        " завершится.\nТы всегда можешь"
        " остановить\перезапустить бота командой\n/stop \nДля начала нажми кнопку ниже:\n",
        reply_markup=keyboard)


@dp.message_handler(state='*', commands=['stop'])
async def cmd_stop(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    if user_id in user_timers:
        user_timers[user_id].cancel()
    await state.finish()
    await message.reply(
        "Бот остановлен. Для начала работы снова введите команду /start")


async def set_default_commands(dp):
    await dp.bot.set_my_commands([
        types.BotCommand('start', 'Начать анкету'),
        types.BotCommand('stop', 'Остановить/перезапустить анкету')
    ])
    await set_default_commands(dp)


@dp.message_handler(text="Начать")
async def start_button_handler(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    await Form.name.set()
    await message.reply("Для начала введи своё имя и фамилию:",
                        reply_markup=ReplyKeyboardRemove())
    await create_task(state, message)


@dp.message_handler(state=Form.name)
async def process_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        user_name = message.text
        data['name'] = user_name
    await create_task(state, message)
    await Form.next()
    datepicker = Datepicker(_get_datepicker_settings())
    markup = datepicker.start_calendar()
    await message.answer("Выбери дату рождения на календаре: ", reply_markup=markup)


@dp.callback_query_handler(Datepicker.datepicker_callback.filter(), state=Form.birth_date)
async def process_birth_date(callback_query: CallbackQuery, callback_data: dict, state: FSMContext):
    datepicker = Datepicker(_get_datepicker_settings())
    _date = await datepicker.process(callback_query, callback_data)
    if _date:
        birthdate = _date.strftime('%m/%d/%Y')
        async with state.proxy() as data:
            data['birth_date'] = birthdate
            user_id = callback_query.message.from_user.id
            if user_id in user_timers:
                user_timers[user_id].cancel()
            # task = asyncio.create_task(name_input_timeout(state, callback_query))
            # user_timers[user_id] = task
            await Form.next()
            keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard.add("Назад")
            await callback_query.message.reply("Введи контактный номер телефона: ", reply_markup=keyboard)

    await callback_query.answer()


@dp.message_handler(state=Form.phone_number)
async def process_phone_number(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        phone_number = message.text
        if phone_number == "Назад":
            await message.answer("Снова введи имя и фамилию")
            await Form.name.set()
        else:
            data['phone_number'] = phone_number
            await create_task(state, message)
            await Form.next()
            keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard.add("Назад")
            await message.reply(
                "Введи ссылку на страницу в ВК, Instagram, Telegram (мы просто хотим поставить 👍):"
                , reply_markup=keyboard)


@dp.message_handler(state=Form.social_links)
async def process_social_links(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        social_links = message.text
        if social_links == "Назад":
            await message.answer("Cнова введи номер телефона:")
            await Form.phone_number.set()
        else:
            data['social_links'] = social_links

            # Создаем объект ReplyKeyboardMarkup и добавляем кнопки
            markup = ReplyKeyboardMarkup(resize_keyboard=True)
            buttons = ['Учусь очно', 'Учусь заочно', 'Закончил/Не учусь', 'Назад']
            # markup.add(KeyboardButton("Учусь очно"), KeyboardButton("Учусь заочно"),
            #            KeyboardButton("Закончил/Не учусь"))
            for item in buttons:
                markup.add(item)
            await create_task(state, message)
            await Form.next()
            await message.reply("На момент заполнения анкеты ты:", reply_markup=markup)


@dp.message_handler(state=Form.education_status)
async def process_current_status(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        education_status = message.text
        if education_status == "Назад":
            await message.answer("Снова введи ссылки на соц.сети: ")
            await Form.social_links.set()
        else:
            data['education_status'] = education_status
            await create_task(state, message)
            await Form.education_details.set()
            keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard.add("Назад")
            await message.reply(
                "Напиши пожалуйста наименование учебного заведения, специальность и год выпуска.",
                reply_markup=keyboard)


@dp.message_handler(state=Form.education_details)
async def process_education_details(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        education_details = message.text
        if education_details == "Назад":
            markup = ReplyKeyboardMarkup(resize_keyboard=True)
            buttons = ['Учусь очно', 'Учусь заочно', 'Закончил/Не учусь', 'Назад']
            # markup.add(KeyboardButton("Учусь очно"), KeyboardButton("Учусь заочно"),
            #            KeyboardButton("Закончил/Не учусь"))
            for item in buttons:
                markup.add(item)
            await message.answer("На момент заполнения анкеты ты:", reply_markup=markup)
            await Form.education_status.set()
        else:
            data['education_details'] = education_details
            markup = ReplyKeyboardMarkup(resize_keyboard=True)
            buttons = ['Да', "Нет", "Назад"]
            for item in buttons:
                markup.add(item)
            await create_task(state, message)
            await Form.is_our_guest.set()
            await message.reply("Являешься ли ты нашим гостем: ", reply_markup=markup)


@dp.message_handler(state=Form.is_our_guest)
async def process_is_guest(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        is_our_guest = message.text
        if is_our_guest == "Назад":
            markup = ReplyKeyboardMarkup(resize_keyboard=True)
            buttons = ['Да', "Нет", "Назад"]
            for item in buttons:
                markup.add(item)
            await message.answer("Напиши пожалуйста наименование учебного заведения, специальность и год выпуска.")
            await Form.education_details.set()
        else:
            data['is_our_guest'] = is_our_guest
            keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard.add("Назад")
            await message.reply("Что для тебя важно при выборе работы?",
                                reply_markup=keyboard)
            await create_task(state, message)
            await Form.user_link.set()


@dp.message_handler(state=Form.user_link)
async def start_command(message: types.Message, state: FSMContext):
    user_link = f'https://t.me/{message.from_user.username}'
    async with state.proxy() as data:
        job_preferences = message.text
        if job_preferences == "Назад":
            markup = ReplyKeyboardMarkup(resize_keyboard=True)
            buttons = ['Да', "Нет", "Назад"]
            for item in buttons:
                markup.add(item)
            await message.answer("Являешься ли ты нашим гостем: ", reply_markup=markup)
            await Form.is_our_guest.set()
        else:
            data['job_preferences'] = message.text
            data['user_link'] = user_link
            await create_task(state, message)
            keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard.add("Назад")
            await Form.job_preferences.set()
            await message.reply("Идём дальше ?", reply_markup=keyboard)


@dp.message_handler(state=Form.job_preferences)
async def process_job_preferences(message: types.Message, state: FSMContext):
    social_links = message.text
    if social_links == "Назад":
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add("Назад")
        await message.reply("Что для тебя важно при выборе работы?",
                            reply_markup=keyboard)
        await Form.user_link.set()
    else:
        await create_task(state, message)
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add("Назад")
        await Form.last_job.set()
        await message.reply("Предыдущее место работы?(не официальное тоже считается)"
                            , reply_markup=keyboard)


@dp.message_handler(state=Form.last_job)
async def process_last_job(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        social_links = message.text
        if social_links == "Назад":
            keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard.add("Назад")
            await message.reply("Что для тебя важно при выборе работы?",
                                reply_markup=keyboard)
            await Form.user_link.set()
        else:
            data['last_job'] = message.text
            await create_task(state, message)
            await Form.dismissal_reason.set()
            await message.reply("Причина ухода с предыдущего места работы?")


@dp.message_handler(state=Form.dismissal_reason)
async def process_dismissal_reason(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['dismissal_reason'] = message.text
    await create_task(state, message)
    await Form.why_us.set()
    await message.reply(
        "Почему ты хочешь работать с кофе и выбираешь именно нашу компанию? (Мы конечно догадываемся, но все же)"
    )


@dp.message_handler(state=Form.why_us)
async def process_why_us(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['why_us'] = message.text
    await Form.main_dream.set()
    await message.reply("Какая твоя главная мечта?",
                        reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(state=Form.main_dream)
async def process_main_dream(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['main_dream'] = message.text
    await create_task(state, message)
    await Form.favorite_drink.set()
    await message.reply("Какой твой любимый напиток?")


@dp.message_handler(state=Form.favorite_drink)
async def process_favorite_drink(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['favorite_drink'] = message.text
    await create_task(state, message)
    await Form.new_acquaintances.set()
    await message.reply(
        "Ты легко находишь общий язык с людьми, заводишь новые знакомства?")


@dp.message_handler(state=Form.new_acquaintances)
async def process_new_acquaintances(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['new_acquaintances'] = message.text
    await create_task(state, message)
    await Form.emotions.set()
    await message.reply("Бывает сложно сдерживать эмоции?")


@dp.message_handler(state=Form.emotions)
async def process_emotions(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['emotions'] = message.text
    await create_task(state, message)
    await Form.work_schedule.set()
    await message.reply("Желаемый график работы?")


@dp.message_handler(state=Form.work_schedule)
async def process_work_schedule(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['work_schedule'] = message.text
    await create_task(state, message)
    await Form.last_job_recommendation.set()
    await message.reply(
        "Кто может порекомендовать тебя с предыдущего места работы? (телефон, ФИО)"
    )


@dp.message_handler(state=Form.last_job_recommendation)
async def process_last_job_recommendation(message: types.Message,
                                          state: FSMContext):
    async with state.proxy() as data:
        data['last_job_recommendation'] = message.text
    await create_task(state, message)
    await Form.know_vacancy.set()
    await message.reply("Как ты узнал о вакансии?")


@dp.message_handler(state=Form.know_vacancy)
async def process_know_vacancy(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['know_vacancy'] = message.text
    await create_task(state, message)
    await Form.if_you_small.set()
    await message.reply(
        "Представь: ты в комнате, там стоит большой стол, а на столе стоит твоя любимая еда. Ты до жути голодный. Но есть одно "
        "но"
        ", ты маленького роста, размером с мышку. Что ты будешь делать?")


@dp.message_handler(state=Form.if_you_small)
async def process_if_you_small(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['if_you_small'] = message.text
    await create_task(state, message)
    await Form.remark.set()
    await message.reply(
        "Как ты отреагируешь на замечание коллеги на твою работу?")


@dp.message_handler(state=Form.remark)
async def process_remark(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['remark'] = message.text

    options = [
        "Предлагать и продвигать новые методы и решения",
        "Работать по инструкции/регламенту", "Другое (напиши текстом)"
    ]
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    for option in options:
        markup.add(KeyboardButton(option))
    await create_task(state, message)
    await Form.what_closely.set()
    await message.reply("Выберите вариант или введите свой ответ:",
                        reply_markup=markup)


@dp.message_handler(state=Form.what_closely)
async def process_what_closely(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['what_closely'] = message.text
    await create_task(state, message)
    await Form.freeze_pinguin.set()
    await message.reply(
        "Ты приходишь домой, и видишь в своей морозилке пингвина. Твои действия?",
        reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(state=Form.freeze_pinguin)
async def process_freeze_pinguin(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['freeze_pinguin'] = message.text
    await create_task(state, message)
    await Form.theft.set()
    await message.reply(
        "Коллега украл/а имущество компании, ты — свидетель. Что будешь делать с этой информацией?"
    )


@dp.message_handler(state=Form.theft)
async def process_theft(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['theft'] = message.text
    await create_task(state, message)
    await Form.next()
    await message.reply(
        "Тебе предложили работу два работодателя. Как будешь выбирать?")


@dp.message_handler(state=Form.two_employers)
async def process_two_employers(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        await create_task(state, message)
        today = date.today()
        timestamp = today.strftime("%m/%d/%Y")
        data['timestamp'] = timestamp
        data['two_employers'] = message.text

        text = "Новая анкета:\n\n"
        text += f"Ссылка на телеграмм: {data.get('user_link')}\n \n"
        text += f"Имя и фамилия: {data.get('name')}\n \n"
        text += f"Дата рождения: {data.get('birth_date')}\n \n"
        text += f"Контактный номер телефона: {data.get('phone_number')}\n \n"
        text += f"Ссылки на социальные сети: {data.get('social_links')}\n \n"
        text += f"На момент заполнения анкеты ты: {data.get('education_status')}\n \n"
        text += f"Учебное заведение: {data.get('education_details')}\n \n"
        text += f"Наш гость: {data.get('is_our_guest')}\n \n"
        text += f"Приоритеты в работе: {data.get('job_preferences')}\n \n"
        text += f"Предыдущее место работы: {data.get('last_job')}\n \n"
        text += f"Причина ухода: {data.get('dismissal_reason')}\n \n"
        text += f"Почему хочешь работать с кофе и у нас: {data.get('why_us')}\n \n"
        text += f"Главная мечта: {data.get('main_dream')}\n \n"
        text += f"Любимый напиток: {data.get('favorite_drink')}\n \n"
        text += f"Легко заводишь знакомства: {data.get('new_acquaintances')}\n \n"
        text += f"Сложно ли сдерживать эмоции: {data.get('emotions')}\n \n"
        text += f"График работы: {data.get('work_schedule')}\n \n"
        text += f"Кто может порекомендовать с прошлого места работы: {data.get('last_job_recommendation')}\n \n"
        text += f"Как узнал о вакансии: {data.get('know_vacancy')}\n \n"
        text += f"Комната, стол, еда, ты маленький: {data.get('if_you_small')}\n \n"
        text += f"Реакция на замечание коллеги: {data.get('remark')}\n \n"
        text += f"Что ближе: {data.get('what_closely')}\n \n"
        text += f"Пингвин в морозилке: {data.get('freeze_pinguin')}\n \n"
        text += f"Коллега вор, ты свидетель, варианты: {data.get('theft')}\n \n"
        text += f"Предложили работу двое, как будешь выбирать: {data.get('two_employers')}\n \n"

        await message.reply("Анкета формируется, подожди минутку пожалуйста")
        user_id = message.from_user.id
        if user_id in user_timers:
            user_timers[user_id].cancel()
        last_row = get_last_processed_row(LAST_PROCESSED_ROW_FILE)

        worksheet.update(f"A{last_row}", str(data.get('timestamp')))
        worksheet.update(f"B{last_row}", data.get('name'))
        worksheet.update(f"C{last_row}", data.get('birth_date'))
        worksheet.update(f"D{last_row}", data.get('phone_number'))
        worksheet.update(f"E{last_row}", data.get('social_links'))
        worksheet.update(f"F{last_row}", data.get('education_status'))
        worksheet.update(f"G{last_row}", data.get('education_details'))
        worksheet.update(f"H{last_row}", data.get('is_our_guest'))
        worksheet.update(f"I{last_row}", data.get('job_preferences'))
        worksheet.update(f"J{last_row}", data.get('last_job'))
        worksheet.update(f"K{last_row}", data.get('dismissal_reason'))
        worksheet.update(f"L{last_row}", data.get('why_us'))
        worksheet.update(f"M{last_row}", data.get('main_dream'))
        worksheet.update(f"N{last_row}", data.get('favorite_drink'))
        worksheet.update(f"O{last_row}", data.get('new_acquaintances'))
        worksheet.update(f"P{last_row}", data.get('emotions'))
        worksheet.update(f"Q{last_row}", data.get('work_schedule'))
        worksheet.update(f"R{last_row}", data.get('last_job_recommendation'))
        worksheet.update(f"S{last_row}", data.get('know_vacancy'))
        worksheet.update(f"T{last_row}", data.get('if_you_small'))
        worksheet.update(f"U{last_row}", data.get('remark'))
        worksheet.update(f"V{last_row}", data.get('what_closely'))
        worksheet.update(f"W{last_row}", data.get('freeze_pinguin'))
        worksheet.update(f"X{last_row}", data.get('theft'))
        worksheet.update(f"Y{last_row}", data.get('two_employers'))
        last_row += 1
        update_last_processed_row(last_row, LAST_PROCESSED_ROW_FILE)

        await bot.send_message(chat_id="-1001609605973", text=text)
        await state.finish()

    await message.reply(
        "Спасибо, что заполнил анкету для устройства на работу в Coffee Like KMS, красавчик! Совсем скоро в твою дверь постучатся... А точнее, свяжутся с тобой в WhatsApp, Telegram или позвонят, если анкета будет одобрена. Хорошего тебе дня и отличного настроения!"
    )


# keep_alive()
if __name__ == '__main__':
    set_commands(dp)
    executor.start_polling(dp, skip_updates=True)
