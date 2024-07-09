from aiogram import types, F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
import keyboards as kb
from middlewares import AuthorizeMiddleware
from database.models import User
from .states import TopUpBalanceWithCard, WithdrawBalance, EnterPromocode
from aiogram.fsm.context import FSMContext


router = Router()
router.message.middleware(AuthorizeMiddleware())
router.callback_query.middleware(AuthorizeMiddleware())


@router.callback_query(F.data == 'wallet')
async def cmd_open_wallet(cb: CallbackQuery, user: User):
    text = f'''
💰 Ваш кошелек:
🆔 Твой пользовательский ID: {user.tg_id}
🏦 Баланс: {user.balance} UAH'''
    await cb.message.edit_text(text, reply_markup=kb.get_wallet_kb())

@router.callback_query(F.data == 'top_up')
async def cmd_top_up(cb: CallbackQuery):
    text = "ℹ️ Выберите метод оплаты:"
    await cb.message.edit_text(text, reply_markup=kb.get_top_up_kb())

@router.callback_query(F.data == 'card')
async def top_up_with_card(cb: CallbackQuery, state: FSMContext):
    await state.set_state(TopUpBalanceWithCard.wait_amount)
    await cb.message.edit_text("❔ Введите сумму для пополнения:")

@router.message(F.text, TopUpBalanceWithCard.wait_amount)
async def set_amount(message: Message, state: FSMContext, user: User):
    await state.clear()
    await message.answer(f'''🤵 Для пополнения баланса

💳 Реквизиты : 5375524800614054
💬 Комментарий : BLI-ZATO:{user.tg_id}

⚠️Реквизиты действительны в течении 20 минут после запроса, если вы не успели оплатить в течении указанного времени сделайте ещё один запрос реквизитов.⚠️

⚠️Нажмите на реквизиты или комментарий, чтобы скопировать!

⚠️Если вы не можете указать комментарий, после оплаты пришлите чек/скриншот или же квитанцию в техническую поддержку.

⚠️ 🛠 Тех.Поддержка - @OKXsupport_official

С уважением. OKX Trading''', reply_markup=kb.get_support_kb())
    
@router.callback_query(F.data == 'crypto')
async def top_up_with_crypto(cb: CallbackQuery):
    await cb.message.edit_text("Выберите криптовалюту:", 
                               reply_markup=kb.get_select_crypto_currency_kb())
    
@router.callback_query(F.data.startswith('crypto_currency_'))
async def pay_with_crypto(cb: CallbackQuery):
    crypto_min_prices = {
        'btc': 0.001,
        'eth': 0.015,
        'usdt': 20,
    }

    currency = cb.data.split('_')[-1]
    text = f'''
    📍 Для вашего удобства предоставляем возможность пополнения баланса через\
{currency.upper()}. Пожалуйста, отправьте любую сумму от {crypto_min_prices[currency]} {currency.upper()} на уникальный адрес:

bc1qsq7kqn380fvgtwf98x9t2w6swgztl4ceerau8j

Наш бот автоматически пересчитает актуальный курс BTC и зачислит средства на ваш баланс после первого подтверждения в сети.\
После пополнения вы получите уведомление о зачислении средств 🚀

Благодарим за выбор наших услуг! При вопросах обращайтесь к нашей поддержке. 🌐'''
    await cb.message.edit_text(text, reply_markup=kb.get_support_kb())

@router.callback_query(F.data == 'withdraw')
async def cmd_withdraw(cb: CallbackQuery, state: FSMContext):
    await cb.message.edit_text("❔ Введите сумму для вывода:", reply_markup=kb.get_back_kb())
    await state.set_state(WithdrawBalance.wait_amount)

@router.message(F.text, WithdrawBalance.wait_amount)
async def set_amount_of_withdraw(message: Message, state: FSMContext, user: User):
    #await state.clear()
    await message.answer('''❌ Ошибка
💸Введите сумму для вывода:''')
    

@router.callback_query(F.data == 'promocode')
async def cmd_promocode(cb: CallbackQuery, state: FSMContext):
    text = "❔ Введите промокод:"
    await cb.message.edit_text(text, reply_markup=kb.get_back_kb())
    await state.set_state(EnterPromocode.wait_promocode)

@router.message(F.text, EnterPromocode.wait_promocode)
async def set_promocode(message: Message, state: FSMContext, user: User):
    await state.clear()
    await message.answer("❌ Данного промокода не существует")


@router.callback_query(F.data == 'check_payment')
async def cmd_check_payment(cb: CallbackQuery):
    await cb.message.edit_text(
        "💸Деньги будут зачислены на ваш счет автоматически сразу после оплаты",
        reply_markup=kb.get_back_kb())