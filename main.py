import logging
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InputFile
from aiogram.utils import executor
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from PIL import Image, ImageFont, ImageDraw
import time
sample = Image.open('r1.png')

# Настройки бота
API_TOKEN = 'ENTER TOKEN'

# Настройки базы данных
DATABASE_URL = 'sqlite:///store.db'
engine = create_engine(DATABASE_URL, echo=True)
Base = declarative_base()


# Модель товара
class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    price = Column(Integer)


# Инициализация бота
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Создание сессии SQLAlchemy
Session = sessionmaker(bind=engine)
session = Session()


# Определение состояний
class ShopStates(StatesGroup):
    selecting_product = State()
    entering_quantity = State()


# Обработчик команды /start
@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    # Загрузка товаров из базы данных
    products = session.query(Product).all()

    # Создание клавиатуры с товарами
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for product in products:
        keyboard.add(types.KeyboardButton(product.name))

    await message.answer("Добро пожаловать в наш магазин! Выберите товар:", reply_markup=keyboard)

    # Установка состояния selecting_product
    await ShopStates.selecting_product.set()

@dp.message_handler(text='фото')
async def cmd_start(message: types.Message):
        await message.answer_photo(photo='mO9npDkSYs0.jpg', caption='фото с компа')

# @dp.message_handler(content_types=['photo'])
# async def handle_docs_photo(message):
#     await message.photo[-1].download('r1.png')
#     time.sleep(1)
#     sample = Image.open('r1.png')
#     cord = (10, 10, 640, 340)  # лево, верх, право, низ
#     new_picture = sample.crop(cord)
#     new_picture.show()

@dp.message_handler(content_types=['photo'])
async def handle_docs_photo(message: types.Message):
    await message.photo[-1].download('r1.png')
    time.sleep(1)
    sample = Image.open('r1.png')
    font = ImageFont.truetype('Minecraft.otf', size=20, encoding='ASCII')
    draw = ImageDraw.Draw(sample)
    draw.text((0, 0), font=font, text="Hello world", align="center", fill='blue')
    sample.save('r3.png')
    sample1 = Image.open('r1.png')
    font1 = ImageFont.truetype('tahoma.ttf', size=20, encoding='ASCII')
    draw1 = ImageDraw.Draw(sample1)
    draw1.text((0, 0), font=font1, text="Hello world", align="center", fill='red')
    sample1.save('r2.png')
    await message.answer_photo(InputFile('r3.png'))
    await message.answer_photo(InputFile('r2.png'))

# уменьшил размер изображения в два раза
    resized_image = sample.resize((262, 372))
    resized_image.save('resized_r1.png')
    await message.answer_photo(InputFile('resized_r1.png'))

# Обработчик выбора товара
@dp.message_handler(state=ShopStates.selecting_product)
async def process_product_selection(message: types.Message, state: FSMContext):
    product_name = message.text

    # Получение выбранного товара
    product = session.query(Product).filter(Product.name == product_name).first()
    if not product:
        await message.answer("Извините, этот товар не найден. Попробуйте еще раз.")
        return

    # Сохранение выбранного товара в контексте пользователя
    await state.update_data(product_id=product.id)

    # Переход к следующему состоянию entering_quantity
    await message.answer("Выберите количество товара:")
    await ShopStates.entering_quantity.set()

# Обработчик ввода количества товара
@dp.message_handler(state=ShopStates.entering_quantity)
async def process_quantity_entry(message: types.Message, state: FSMContext):
    quantity = int(message.text)

    # Получение выбранного товара из контекста пользователя
    data = await state.get_data()
    product_id = data.get('product_id')

    # Получение информации о товаре
    product = session.query(Product).filter(Product.id == product_id).first()

    # Имитация покупки товара
    total_price = product.price * quantity

    # Отправка сообщения о покупке
    await message.answer(f"Вы купили {product.name} в количестве {quantity} шт.\n"
                         f"Общая стоимость: {total_price} руб.")

    # Возвращение к начальному состоянию
    await state.finish()


if __name__ == '__main__':
    # Создание таблицы товаров в базе данных
    Base.metadata.create_all(engine)

    # Запуск бота
    executor.start_polling(dp, skip_updates=True)
