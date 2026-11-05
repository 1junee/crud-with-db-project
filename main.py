from sqlalchemy import create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse

DB_URL = "postgresql+psycopg://sd4:sd4@localhost:5432/board"
# engine = create_engine(DB_URL)          # 기본: SQL 로그 출력 안 함
engine = create_engine(DB_URL, echo=True)  # echo=True: 실행되는 SQL을 터미널에 출력 (학습용)

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
        # Post 클래스에 연결된 posts 테이블 전체 조회 (SELECT * FROM posts)
        # .all()로 실행해서 Post 객체 리스트로 받음
        posts = db.scalars(select(Post)).all()
        return templates.TemplateResponse(
            request=request,
            name='list.html',
            context={'posts': posts}
        )


@app.get('/posts/{post_id}')
def post_detail(post_id: int, request: Request):
    with Session(engine) as db:
        # 기본키로 하나 조회 (SELECT ... WHERE id = post_id), 없으면 None
        # 조회 결과(post 객체)는 세션이 닫혀도 파이썬 변수로 남아 있어서 with 밖에서도 사용 가능
        # with 문이 끝나면 세션(DB 연결)이 닫힘 → db 변수 이름은 남지만 더 이상 DB 작업은 못 함
        post = db.get(Post, post_id) 
        # 100번 게시물 접근하려 할 떄 None 반환 -> 에러 없이 작동은 됨 -> 예외 처리 필요
        # print(post)
        if post is None:
            return RedirectResponse('/posts', status_code=303)

    return templates.TemplateResponse(
        request=request,
        name='detail.html',
        context={'post': post}
    )

