# create_engine: DB 연결 통로 생성 / select: SELECT 문 생성
from sqlalchemy import create_engine, select
# DeclarativeBase: ORM 부모 클래스 / Mapped: 컬럼 타입 표시 / mapped_column: 컬럼 옵션 / Session: DB 작업 단위
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session

#        "DB종류     +드라이버://사용자:비밀번호@서버:포트/DB이름
DB_URL = "postgresql+psycopg://sd4:sd4@localhost:5432/board"
# 연결 통로 준비 (실제 접속은 처음 쓸 때) / echo=True: 실행되는 SQL을 터미널에 출력
engine = create_engine(DB_URL, echo=True)


# 모든 테이블 클래스의 공통 부모
class Base(DeclarativeBase):
    pass


# sqlalchemy의 설명서 대로 작성
# Post 클래스 = posts 테이블, Post 객체 하나 = 한 줄(row)
class Post(Base):
    # posts 테이블과 Post 클래스를 연결 (매핑)
    __tablename__ = 'posts'

    # posts 테이블의 속성값과 연결 (변수 이름 = 컬럼 이름)
    id: Mapped[int] = mapped_column(primary_key=True)  # 기본키, DB가 자동 증가
    title: Mapped[str]                                 # str → NOT NULL 문자열
    content: Mapped[str]


# db에 접속한다
# with문이 끝나면 닫는다 (에러가 나도 자동으로 닫힘)
with Session(engine) as db:
    # select(Post) → SELECT * FROM posts / scalars → Post 객체로 / all → 리스트로
    posts = db.scalars(select(Post)).all()

    print(type(posts), len(posts), type(posts[0]))
    # 한 줄(row)을 객체 속성처럼 꺼내 씀 → 이게 ORM
    for post in posts:
        print(post.id, post.title, post.content)
