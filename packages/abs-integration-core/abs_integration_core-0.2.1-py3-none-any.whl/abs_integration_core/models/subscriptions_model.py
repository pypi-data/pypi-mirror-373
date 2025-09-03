from sqlalchemy import Column, String, Integer, JSON, DateTime

from abs_repository_core.models import BaseModel


class Subscription(BaseModel):
    __tablename__ = "gov_subscriptions"
    
    target_url = Column(String(255), nullable=False)
    site_id = Column(String(255), nullable=True)
    resource_id = Column(String(255), nullable=True)
    target_path = Column(String(255), nullable=True)
    event_types = Column(JSON, nullable=False)
    provider_name = Column(String(255), nullable=False)
    expires_at = Column(DateTime, nullable=True)

    user_id = Column(Integer, nullable=False)
    integration_id = Column(String(36), nullable=False)

    # user = relationship(Users, backref="subscriptions")
