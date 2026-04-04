"""FSM states for order creation flow."""

from aiogram.fsm.state import State, StatesGroup


class OrderStates(StatesGroup):
    select_format = State()
    send_ad_content = State()
    select_date = State()
    preview = State()


class PaymentStates(StatesGroup):
    waiting_screenshot = State()


class RejectOrderStates(StatesGroup):
    enter_reason = State()
