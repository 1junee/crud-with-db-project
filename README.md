# CRUD DB

FastAPI + PostgreSQL + SQLAlchemy(ORM)로 만든 게시판 CRUD

<br>

## ⚙️ Setting

### 1. 데이터베이스 생성

```bash
# -d: 접속할 DB / postgres: 설치 시 기본으로 있는 관리용 DB (-U 생략 시 Mac 사용자명으로 접속)
psql -d postgres
```

```sql
-- psql 안에서 실행하는 SQL: board DB 생성, 주인(OWNER)은 sd4 사용자 / 끝에 ; 필수
CREATE DATABASE board OWNER sd4;
```

```bash
# -U: 접속할 사용자(대문자 U) / -d: 접속할 DB → sd4로 board에 접속
psql -U sd4 -d board
```

> **psql 안에서 쓰는 명령** (`\`로 시작, `;` 불필요)
>
> | 명령 | 뜻 |
> |---|---|
> | `\l` | DB 목록 |
> | `\c board` | DB 이동 |
> | `\d` | 테이블 목록 |
> | `\d posts` | 테이블 구조 |
> | `\q` | 나가기 |

### 2. uv 프로젝트 생성

```bash
uv init crud-with-db --bare --python 3.14
uv add "fastapi[standard]" sqlalchemy "psycopg[binary]"
```

### 3. 테이블 생성 + 초기 데이터 (`schema.sql`)

```bash
# -f: 파일 안의 SQL을 순서대로 실행하고 종료 (CREATE TABLE, INSERT 한 번에)
psql -U sd4 -d board -f schema.sql
```

<br>

## ▶️ Run Server

```bash
uv run fastapi dev
```

DB 연결 / ORM 확인용 (실행 후 `>>>`에서 `db`, `Post` 직접 사용)

```bash
uv run python -i db_check.py
```

<br>

## 🗺️ 라우트

| 기능 | 메서드 | 주소 | 이동 |
|---|---|---|---|
| 목록 (R) | `GET` | `/posts` | list.html |
| 작성 폼 | `GET` | `/posts/new` | new.html |
| 생성 (C) | `POST` | `/posts/create` | → `/posts/{id}` |
| 상세 (R) | `GET` | `/posts/{id}` | detail.html (없으면 404) |
| 수정 폼 | `GET` | `/posts/{id}/edit` | edit.html |
| 수정 (U) | `POST` | `/posts/{id}/update` | → `/posts/{id}` |
| 삭제 (D) | `POST` | `/posts/{id}/delete` | → `/posts` |

> ⚠️ `/posts/{id}` 상세 라우트는 `/posts/new`보다 **아래**에 둬야 함 (위에 있으면 `new`를 id로 받으려다 422)

<br>

## 🧩 SQLAlchemy 핵심 정리

### ORM이란

- 테이블 = 클래스, 한 줄(row) = 객체로 다루게 해주는 도구 (SQL을 대신 만들어 줌)
- 장점: 파이썬 문법, 자동완성, SQL 인젝션 방지, DB 종류 바꾸기 쉬움
- 단점: 어떤 SQL이 나가는지 안 보임 → `echo=True`로 확인, 복잡한 쿼리는 SQL 직접이 나을 때도 있음

### 구성 요소

| 이름 | 역할 |
|---|---|
| `psycopg` | PostgreSQL과 실제로 통신하는 드라이버 |
| `create_engine` | DB 연결 통로(engine) 생성, 앱에서 **한 번만** (실제 접속은 처음 쓸 때) |
| `DeclarativeBase` | 테이블 클래스들의 공통 부모 |
| `Mapped`, `mapped_column` | 컬럼 정의 (`Mapped[str]` → NOT NULL 문자열, `primary_key=True` → 기본키) |
| `Session` | DB 작업 단위, 요청마다 `with Session(engine) as db:`로 열고 닫음 |

### 접속 주소

```
dialect+driver://username:password@host:port/database
postgresql+psycopg://sd4:sd4@localhost:5432/board
```

- `+psycopg` 생략하면 기본 드라이버 psycopg2를 찾음 → 설치 안 돼 있으면 에러
- 비밀번호에 특수문자(`@`, `/` 등)가 있으면 `URL.create()` 사용
- `echo=True`: SQL 출력 / `echo="debug"`: 결과 행까지 출력

### 객체가 DB에 저장되는 흐름

```python
post = Post(title='t', content='c')   # id=None, 파이썬 객체일 뿐
db.add(post)                          # id=None, 세션에 '저장 예정'으로 등록
db.commit()                           # INSERT 실행 → DB가 만든 id 받아옴
```

- `with` 블록이 끝나면 세션이 닫힘, 이미 읽어온 객체 값은 밖에서도 사용 가능
- `commit()` 없이 끝나면 ROLLBACK (조회만 했을 때 로그에 찍히는 ROLLBACK은 정상)

<br>

## 🔄 ORM vs SQL

> ORM 코드 → SQLAlchemy가 만들어서 DB로 보내는 SQL (`echo=True`로 확인)
> `%(title)s` 자리에는 실제 값이 따로 안전하게 들어감 (SQL 인젝션 방지)

### READ

**전체**

```python
db.scalars(select(Post)).all()
```

```sql
SELECT posts.id, posts.title, posts.content FROM posts
```

**하나** (기본키로 조회, 없으면 `None`)

```python
db.get(Post, 1)
```

```sql
SELECT posts.id, posts.title, posts.content FROM posts WHERE posts.id = %(pk_1)s::INTEGER
```

### CREATE

```python
post = Post(title='test', content='test content')
db.add(post)
db.commit()
```

```sql
INSERT INTO posts (title, content) VALUES ('test', 'test content') RETURNING posts.id;
```

- `RETURNING posts.id`: DB가 자동으로 만든 id를 돌려받아 `post.id`에 채워 줌
- echo 로그에는 값 자리가 `%(title)s`, `%(content)s`로 찍히고, 실제 값은 아래 줄에 따로 나옴

```
INSERT INTO posts (title, content) VALUES (%(title)s::VARCHAR, %(content)s::VARCHAR) RETURNING posts.id
{'title': 'test', 'content': 'test content'}
```

### UPDATE

```python
post = db.get(Post, 1)      # 먼저 꺼내고
post.title = 'new title'    # 속성만 바꾸면
db.commit()                 # commit 때 바뀐 컬럼만 UPDATE
```

```sql
UPDATE posts SET title=%(title)s::VARCHAR WHERE posts.id = %(posts_id)s::INTEGER
```

### DELETE

```python
post = db.get(Post, 1)
db.delete(post)
db.commit()
```

```sql
DELETE FROM posts WHERE posts.id = %(id)s::INTEGER
```

<br>

## 📌 정리

| CRUD | ORM | SQL |
|---|---|---|
| C | `db.add(Post(...))` | `INSERT INTO posts ...` |
| R (전체) | `db.scalars(select(Post)).all()` | `SELECT * FROM posts` |
| R (하나) | `db.get(Post, id)` | `SELECT ... WHERE id = ?` |
| U | 객체 속성 변경 | `UPDATE posts SET ... WHERE id = ?` |
| D | `db.delete(post)` | `DELETE FROM posts WHERE id = ?` |

- `commit()`을 해야 실제로 DB에 저장됨 (안 하면 with문 끝날 때 ROLLBACK)
- update / delete는 ORM이 `WHERE id = ...`를 자동으로 붙여 줌 (SQL로 직접 쓸 땐 WHERE 빠뜨리면 전체가 바뀜)
- `db.get()`은 없는 id면 `None` → 상세/수정/삭제 전에 `None` 검사 후 404 (`HTTPException`)
