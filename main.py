from sqlalchemy import create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates

DB_URL = "postgresql+psycopg://sd4:sd4@localhost:5432/board"
# engine = create_engine(DB_URL)
engine = create_engine(DB_URL, echo=True)

class Base(DeclarativeBase):
    pass

class Post(Base):
    __tablename__ = 'posts'

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    content: Mapped[str]

app = FastAPI()
templates = Jinja2Templates(directory='templates')


@app.get('/')
def home():
    return {'test': 'home test'}


@app.get('/posts')
def posts_list(request: Request):
    with Session(engine) as db:
        # Post 클래스에 연결된 테이블 연결, 
        posts = db.scalars(select(Post)).all()
        return templates.TemplateResponse(
            request=request,
            name='list.html',
            context={'posts': posts}
        )


@app.get('/posts/{post_id}')
def post_detail(post_id: int, request: Request):
    with Session(engine) as db:
        # post에 넣은 건 세션에 관계 없이 저장됨
        # with 문이 끝났을 떈 db라는 게 없어지는 거???
        post = db.get(Post, post_id)

    return templates.TemplateResponse(
        request=request,
        name='detail.html',
        context={'post': post}
    )

