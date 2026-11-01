import os
from datetime import datetime

from dotenv import load_dotenv
from sqlalchemy import String, INTEGER, create_engine, URL, ForeignKey, select
from sqlalchemy.orm import mapped_column, Mapped, DeclarativeBase, Session

from pathlib import Path

from Config.logger_config import log

base_dir = Path(__file__).resolve().parent.parent

DB_PATH = base_dir / "Databases" / "russian_dictionary.db"

load_dotenv()

conn_params = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "admin"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME", "my_database"),
}

url = URL.create(
    drivername="mysql+pymysql",
    username=conn_params["user"],
    password=conn_params["password"],
    host=conn_params["host"],
    database=conn_params["database"],
    query={"charset": "utf8mb4"},
)

engine = create_engine(url, echo=False)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    login: Mapped[str] = mapped_column(String(255), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    registration_date: Mapped[datetime] = mapped_column(default=datetime.now)


class LearnedWords(Base):
    __tablename__ = "learned_words"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    word: Mapped[str] = mapped_column(String(255))
    translation: Mapped[str] = mapped_column(String(255))
    group_name: Mapped[str] = mapped_column(String(255))
    progress: Mapped[int] = mapped_column(default=0)
    last_review: Mapped[datetime] = mapped_column(default=datetime.now)
    is_learned: Mapped[bool] = mapped_column(default=False)

    def __repr__(self) -> str:
        return (f"User(id={self.id!r}, word={self.word!r}, progress={self.progress!r}, last_review={self.last_review!r}"
                f", is_learned={self.is_learned!r})")


Base.metadata.create_all(engine)


def add_user_word(word, trans, user_id, table="general"):
    with Session(engine) as session:
        # Checking if word were added
        # UPGRADE_SETTINGS: IF TRIGGER CANCEL WORD'S PROGRESS
        stmt = select(LearnedWords).where(
            LearnedWords.word == word,
            LearnedWords.user_id == user_id,
            LearnedWords.group_name == table
        )

        existing_word = session.execute(stmt).scalar_one_or_none()

        if existing_word:
            log.info(f"Word '{word}' already added to user: {user_id} in group: '{table}'")
            return

        new_string = LearnedWords(
            word=word,
            translation=trans,
            group_name=table,
            user_id=user_id

        )

        session.add(new_string)
        session.commit()
