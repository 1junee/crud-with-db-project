from sqlalchemy import create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session
from fastapi import FastAPI, Request, HTTPException, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

# 지금은 로컬 -> 실제 서비스에 사용하려면?
DB_URL = "postgresql+psycopg://sd4:sd4@localhost:5432/board"
# engine = create_engine(DB_URL)          # 기본: SQL 로그 출력 안 함
engine = create_engine(DB_URL, echo=True)  # echo=True: 실행되는 SQL을 터미널에 출력 (학습용)

# 모든 테이블 클래스의 공통 부모
class Base(DeclarativeBase):
    pass

# Post 클래스 = posts 테이블, Post 객체 하나 = 한 줄(row)
class Post(Base):
    __tablename__ = 'posts'

    id: Mapped[int] = mapped_column(primary_key=True)  # 기본키, DB가 자동 증가
    title: Mapped[str]
    content: Mapped[str]

app = FastAPI()
templates = Jinja2Templates(directory='templates')
# static 폴더(CSS 등)를 /static 주소로 제공 → base.html이 /static/css/board.css를 불러옴
app.mount('/static', StaticFiles(directory='static'), name='static')


@app.get('/')
def home():
    return {'test': 'home test'}


# [R] 전체 목록
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


# [C-1] 작성 폼: DB 작업 없이 빈 form만 보여줌
@app.get('/posts/new')
def post_new(request: Request):
    return templates.TemplateResponse(
        request=request,
        name='new.html',
    )


# [C-2] 생성 → 저장 후 새 글 상세로 redirect
@app.post('/posts/create')
def post_create(title: str = Form(), content: str = Form()):
    # form에서 받은 title, content로 DB에 새 글 저장 (INSERT)
    # with문이 끝나면 세션이 닫힘 (에러가 나도 자동으로 닫힘)
    with Session(engine) as db:
        # C: 객체 만들고 add → commit 해야 실제 저장
        post = Post(title=title, content=content)
        # print('add 전:', post.id)
        # add 전: None → 아직 파이썬 객체일 뿐, DB와 무관
        db.add(post)
        # print('add 후:', post.id)
        # add 후: None → 세션에 '저장 예정'으로 등록만 됨 (INSERT는 아직 안 나감)
        db.commit()
        # print('commit 후:', post.id)
        # commit 후: 8 → commit 때 INSERT가 실행되고, DB가 자동으로 만든 id를 받아옴
        # 세션이 닫히기 전에 id를 변수에 꺼내둠 (redirect 주소에 사용)
        new_id = post.id
    return RedirectResponse(f'/posts/{new_id}', status_code=303)


# [U-1] 수정 폼: 기존 글을 꺼내서 form에 채워 보여줌
@app.get('/posts/{post_id}/edit')
def post_edit(request: Request, post_id: int):
    with Session(engine) as db:
        post = db.get(Post, post_id)

    # 세션 밖이지만 post는 이미 읽어온 값이라 검사·사용 가능
    if post is None:
        raise HTTPException(status_code=404, detail='게시물이 존재하지 않습니다.')

    return templates.TemplateResponse(
        request=request,
        name='edit.html',
        context={'post': post}
    )       


# [U-2] 수정 → 저장 후 상세로 redirect
# post_id는 주소에서, title·content는 form 본문(Form)에서 받음
@app.post('/posts/{post_id}/update')
def post_update(post_id: int, title: str = Form(), content: str = Form()):
    with Session(engine) as db:
        old_post = db.get(Post, post_id)
        if old_post is None:
            raise HTTPException(status_code=404, detail='게시물이 존재하지 않습니다.') 
        # 객체 속성만 바꾸고 commit하면 바뀐 컬럼만 UPDATE
        old_post.title = title
        old_post.content = content
        db.commit()

    return RedirectResponse(f'/posts/{post_id}', status_code=303)


# [D] 삭제 → 글이 없어졌으니 목록으로 redirect
@app.post('/posts/{post_id}/delete')
# post_id는 주소({post_id})에서 오는 경로 변수 → Form() 붙이면 에러
# Form()은 form 본문(<input name="...">)으로 오는 값에만 사용
def post_delete(post_id: int):
    with Session(engine) as db:
        post = db.get(Post, post_id)
        if post is None:
            raise HTTPException(status_code=404, detail='게시물이 존재하지 않습니다.')
        # D: delete 후 commit
        db.delete(post)
        db.commit()

    return RedirectResponse('/posts', status_code=303)


# [R] 상세
# 라우트는 위에서부터 순서대로 주소를 맞춰봄
# 이 함수가 '/posts/new'보다 위에 있으면 'new'를 post_id로 받으려다 에러(422) → 그래서 아래에 둠
@app.get('/posts/{post_id}')
def post_detail(post_id: int, request: Request):
    with Session(engine) as db:
        # 기본키로 하나 조회 (SELECT ... WHERE id = post_id), 없으면 None
        # 조회 결과(post 객체)는 세션이 닫혀도 파이썬 변수로 남아 있어서 with 밖에서도 사용 가능
        # with 문이 끝나면 세션(DB 연결)이 닫힘 → db 변수 이름은 남지만 더 이상 DB 작업은 못 함
        post = db.get(Post, post_id) 
        # 100번 게시물 접근하려 할 때 None 반환 -> 에러 없이 작동은 됨 -> 예외 처리 필요
        # print(post)
        if post is None:
            # 방법 1) 목록으로 돌려보내기 (사용자는 왜 이동했는지 모름)
            # return RedirectResponse('/posts', status_code=303)
            # 방법 2) 404 에러 응답 → {"detail": "게시물이 존재하지 않습니다."} JSON으로 보임
            raise HTTPException(status_code=404, detail='게시물이 존재하지 않습니다.')
            # 방법 3) 에러 안내용 HTML 페이지 보여주기 (cafe-api의 error_page 방식)
            # return templates.TemplateResponse(에러페이지로)

    return templates.TemplateResponse(
        request=request,
        name='detail.html',
        context={'post': post}
    )