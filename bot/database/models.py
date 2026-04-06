from datetime import datetime, date
from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=True)
    username = Column(String(255), nullable=True)
    phone = Column(String(20), nullable=True)
    card_number = Column(String(20), nullable=True)
    language = Column(String(10), default="uz")
    is_blocked = Column(Boolean, default=False)
    referred_by = Column(BigInteger, nullable=True)  # telegram_id of referrer
    referral_count = Column(Integer, default=0)  # how many users invited
    referral_bonus = Column(Integer, default=0)  # bonus balance in UZS
    terms_accepted = Column(Boolean, default=False)  # accepted terms of service
    created_at = Column(DateTime, default=func.now())

    channels = relationship("Channel", back_populates="owner")
    orders = relationship("Order", back_populates="advertiser")

    def __repr__(self):
        return f"<User {self.telegram_id} ({self.full_name})>"


class Region(Base):
    __tablename__ = "regions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name_uz = Column(String(100), nullable=False)
    name_ru = Column(String(100), nullable=False)
    emoji = Column(String(10), default="📍")
    sort_order = Column(Integer, default=0)

    districts = relationship("District", back_populates="region", order_by="District.sort_order")

    def __repr__(self):
        return f"<Region {self.name_uz}>"


class District(Base):
    __tablename__ = "districts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    region_id = Column(Integer, ForeignKey("regions.id"), nullable=False)
    name_uz = Column(String(100), nullable=False)
    name_ru = Column(String(100), nullable=False)
    sort_order = Column(Integer, default=0)

    region = relationship("Region", back_populates="districts")
    channels = relationship("Channel", back_populates="district")

    def __repr__(self):
        return f"<District {self.name_uz}>"


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name_uz = Column(String(100), nullable=False)
    name_ru = Column(String(100), nullable=False)
    emoji = Column(String(10), default="📁")
    sort_order = Column(Integer, default=0)

    channels = relationship("Channel", back_populates="category")

    def __repr__(self):
        return f"<Category {self.emoji} {self.name_uz}>"


class Channel(Base):
    __tablename__ = "channels"

    id = Column(Integer, primary_key=True, autoincrement=True)
    owner_telegram_id = Column(BigInteger, ForeignKey("users.telegram_id"), nullable=False)
    district_id = Column(Integer, ForeignKey("districts.id"), nullable=True)  # NULL = whole region/country
    region_id = Column(Integer, ForeignKey("regions.id"), nullable=True)  # for region-level assignment
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    channel_username = Column(String(255), nullable=False)
    channel_title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    subscribers_count = Column(Integer, default=0)
    avg_views = Column(Integer, default=0)
    avg_rating = Column(Float, default=0.0)  # 0-5
    rating_count = Column(Integer, default=0)
    is_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    is_group = Column(Boolean, default=False)  # True = group, False = channel
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    owner = relationship("User", back_populates="channels")
    district = relationship("District", back_populates="channels")
    category = relationship("Category", back_populates="channels")
    pricing = relationship(
        "ChannelPricing", back_populates="channel", cascade="all, delete-orphan"
    )
    orders = relationship("Order", back_populates="channel")

    def __repr__(self):
        return f"<Channel @{self.channel_username}>"


class AdFormat(Base):
    __tablename__ = "ad_formats"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name_uz = Column(String(100), nullable=False)
    name_ru = Column(String(100), nullable=False)
    description_uz = Column(String(255), nullable=True)
    description_ru = Column(String(255), nullable=True)
    sort_order = Column(Integer, default=0)

    pricing = relationship("ChannelPricing", back_populates="ad_format")

    def __repr__(self):
        return f"<AdFormat {self.name_uz}>"


class ChannelPricing(Base):
    __tablename__ = "channel_pricing"

    id = Column(Integer, primary_key=True, autoincrement=True)
    channel_id = Column(Integer, ForeignKey("channels.id", ondelete="CASCADE"), nullable=False)
    ad_format_id = Column(Integer, ForeignKey("ad_formats.id"), nullable=False)
    price = Column(Integer, nullable=False)  # UZS

    channel = relationship("Channel", back_populates="pricing")
    ad_format = relationship("AdFormat", back_populates="pricing")

    def __repr__(self):
        return f"<Pricing ch={self.channel_id} fmt={self.ad_format_id} price={self.price}>"


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    advertiser_telegram_id = Column(
        BigInteger, ForeignKey("users.telegram_id"), nullable=False
    )
    channel_id = Column(Integer, ForeignKey("channels.id"), nullable=False)
    ad_format_id = Column(Integer, ForeignKey("ad_formats.id"), nullable=False)
    ad_text = Column(Text, nullable=True)
    ad_media_file_id = Column(String(255), nullable=True)
    ad_media_type = Column(String(20), nullable=True)  # photo, video, document
    status = Column(String(20), default="pending", index=True)
    # statuses: pending -> accepted -> payment_pending -> paid -> published -> completed
    #           pending -> rejected
    #           pending -> cancelled (by advertiser)
    price = Column(Integer, nullable=False)  # UZS
    discount = Column(Integer, default=0)  # promo discount amount
    promo_code = Column(String(50), nullable=True)
    desired_date = Column(Date, nullable=True)
    payment_screenshot_file_id = Column(String(255), nullable=True)
    rejection_reason = Column(Text, nullable=True)
    rating = Column(Integer, nullable=True)  # 1-5 stars
    post_views = Column(Integer, nullable=True)  # report: views after publish
    post_reach = Column(Integer, nullable=True)  # report: reach after publish
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    advertiser = relationship("User", back_populates="orders")
    channel = relationship("Channel", back_populates="orders")
    ad_format = relationship("AdFormat")

    def __repr__(self):
        return f"<Order #{self.id} status={self.status}>"


class MonthlyCommission(Base):
    __tablename__ = "monthly_commissions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    owner_telegram_id = Column(BigInteger, ForeignKey("users.telegram_id"), nullable=False)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)  # 1-12
    total_income = Column(Integer, default=0)  # UZS
    commission_amount = Column(Integer, default=0)  # 5% of total_income
    is_paid = Column(Boolean, default=False)
    payment_screenshot_file_id = Column(String(255), nullable=True)
    paid_at = Column(DateTime, nullable=True)
    due_date = Column(Date, nullable=True)  # deadline to pay
    created_at = Column(DateTime, default=func.now())

    owner = relationship("User")

    def __repr__(self):
        return f"<Commission {self.owner_telegram_id} {self.year}/{self.month} paid={self.is_paid}>"


class PromoCode(Base):
    __tablename__ = "promo_codes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    discount_percent = Column(Integer, default=0)  # e.g. 10 = 10%
    discount_amount = Column(Integer, default=0)  # fixed UZS discount
    max_uses = Column(Integer, default=0)  # 0 = unlimited
    used_count = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now())

    def __repr__(self):
        return f"<PromoCode {self.code}>"


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    advertiser_telegram_id = Column(
        BigInteger, ForeignKey("users.telegram_id"), nullable=False
    )
    channel_id = Column(Integer, ForeignKey("channels.id"), nullable=False)
    ad_format_id = Column(Integer, ForeignKey("ad_formats.id"), nullable=False)
    ad_text = Column(Text, nullable=True)
    ad_media_file_id = Column(String(255), nullable=True)
    ad_media_type = Column(String(20), nullable=True)
    price_per_post = Column(Integer, nullable=False)
    frequency = Column(String(20), default="weekly")  # weekly, biweekly, monthly
    is_active = Column(Boolean, default=True)
    next_post_date = Column(Date, nullable=True)
    total_posts = Column(Integer, default=0)  # how many times posted
    created_at = Column(DateTime, default=func.now())

    advertiser = relationship("User")
    channel = relationship("Channel")
    ad_format = relationship("AdFormat")

    def __repr__(self):
        return f"<Subscription #{self.id} ch={self.channel_id} active={self.is_active}>"
