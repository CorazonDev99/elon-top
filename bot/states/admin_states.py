"""FSM states for admin panel."""

from aiogram.fsm.state import State, StatesGroup


class AdminStates(StatesGroup):
    broadcast_text = State()
    broadcast_confirm = State()
    reject_channel_reason = State()


class CommissionPaymentStates(StatesGroup):
    waiting_screenshot = State()
