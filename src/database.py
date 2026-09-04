import os

from sqlalchemy import create_engine, Column, Integer, Float, String
from sqlalchemy.orm import declarative_base, sessionmaker


# --------------------------------------------------
# DATABASE PATH
# --------------------------------------------------

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

DATABASE_DIR = os.path.join(
    BASE_DIR,
    "database"
)

os.makedirs(
    DATABASE_DIR,
    exist_ok=True
)

DATABASE_PATH = os.path.join(
    DATABASE_DIR,
    "reviveai.db"
)

DATABASE_URL = f"sqlite:///{DATABASE_PATH}"


# --------------------------------------------------
# DATABASE ENGINE
# --------------------------------------------------

engine = create_engine(
    DATABASE_URL,
    echo=False
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)

Base = declarative_base()


# --------------------------------------------------
# INVOICE TABLE
# --------------------------------------------------

class Invoice(Base):

    __tablename__ = "invoices"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    customer_id = Column(String)

    invoice_id = Column(
        String,
        unique=True
    )

    invoice_amount = Column(Float)

    invoice_date = Column(String)

    due_date = Column(String)

    payment_date = Column(String)

    payment_status = Column(String)

    days_overdue = Column(Integer)

    previous_payments = Column(Integer)

    previous_late_payments = Column(Integer)

    average_payment_delay = Column(Float)

    payment_failures = Column(Integer)

    communication_count = Column(Integer)

    last_contact_days = Column(Integer)

    discount_used = Column(Integer)

    recovered = Column(Integer)

    customer_segment = Column(String)

    customer_lifetime_value = Column(Float)


# --------------------------------------------------
# RECOVERY OPPORTUNITY TABLE
# --------------------------------------------------

class RecoveryOpportunity(Base):

    __tablename__ = "recovery_opportunities"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    customer_id = Column(String)

    invoice_id = Column(String)

    invoice_amount = Column(Float)

    days_overdue = Column(Integer)

    recovery_probability = Column(Float)

    recovery_probability_percent = Column(Float)

    expected_recovery = Column(Float)

    potential_loss = Column(Float)

    risk_level = Column(String)

    priority_score = Column(Float)

    priority_category = Column(String)

    recommended_action = Column(String)

    customer_segment = Column(String)

    customer_lifetime_value = Column(Float)


# --------------------------------------------------
# RECOVERY TRACKING TABLE
# --------------------------------------------------

class RecoveryTracking(Base):

    __tablename__ = "recovery_tracking"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    # Invoice and customer information
    invoice_id = Column(
        String,
        nullable=False
    )

    customer_id = Column(
        String,
        nullable=False
    )

    # AI recommended action
    recommended_action = Column(String)

    # Actual action taken by recovery team
    actual_action = Column(String)

    # Date on which action was taken
    action_date = Column(String)

    # Current recovery status
    recovery_status = Column(String)

    # Amount actually recovered
    recovered_amount = Column(
        Float,
        default=0
    )

    # Date on which payment was recovered
    recovery_date = Column(String)

    # Next follow-up date
    next_followup_date = Column(String)

    # Additional notes
    notes = Column(String)

    # Record creation timestamp
    created_at = Column(String)


# --------------------------------------------------
# CREATE TABLES
# --------------------------------------------------

def create_tables():

    Base.metadata.create_all(
        engine
    )

    print(
        "Database tables created successfully."
    )


# --------------------------------------------------
# TEST DATABASE
# --------------------------------------------------

if __name__ == "__main__":

    create_tables()

    print()

    print("REVIVEAI DATABASE")
    print("-----------------")

    print(
        "Database created at:"
    )

    print(
        DATABASE_PATH
    )

    print()

    print(
        "Available tables:"
    )

    print(
        "1. invoices"
    )

    print(
        "2. recovery_opportunities"
    )

    print(
        "3. recovery_tracking"
    )

    print()

    print(
        "Recovery tracking table is ready."
    )