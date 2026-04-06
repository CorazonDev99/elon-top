"""FSM states for channel registration flow."""

from aiogram.fsm.state import State, StatesGroup


class ChannelRegStates(StatesGroup):
    enter_username = State()
    enter_card_number = State()
    select_region = State()
    select_district = State()
    select_category = State()
    enter_subscribers = State()
    enter_views = State()
    enter_description = State()
    set_price = State()  # loops through formats


class EditPriceStates(StatesGroup):
    set_price = State()  # loops through formats for editing
