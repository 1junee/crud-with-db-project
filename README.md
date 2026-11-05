# CRUD DB

## setting
- 데이터 베이스 생성
```
psql -d postgres
postgres-# create database board owner sd4;

psql -U sd4 -d board
```

- uv 프로젝트 생성
```
uv init crud_with_db --bare --python 3.14
```


```
uv add "fastapi[standard]" sqlalchemy "
psycopg[binary]"
```

## ORM vs SQL

> ORM 코드 → (=>) SQLAlchemy가 만들어서 DB로 보내는 SQL (`echo=True`로 확인)
> `%(title)s` 자리에는 실제 값이 따로 안전하게 들어감 (SQL 인젝션 방지)

- READ
```
# 전체
db.scalars(select(Post)).all()

=> SELECT posts.id, posts.title, posts.content FROM posts


# 하나 (기본키로 조회, 없으면 None)
db.get(Post, 1)

=> SELECT posts.id, posts.title, posts.content FROM posts WHERE posts.id = %(pk_1)s::INTEGER

```

- CREATE
```
post = Post(title='test', content='test content')
db.add(post)
db.commit()

=> INSERT INTO posts (title, content) VALUES ('test', 'test content') RETURNING posts.id;

# RETURNING posts.id: DB가 자동으로 만든 id를 돌려받아 post.id에 채워 줌
# (echo 로그에는 값 자리가 %(title)s, %(content)s로 찍히고, 실제 값은 아래 줄에 따로 나옴)
#  INSERT INTO posts (title, content) VALUES (%(title)s::VARCHAR, %(content)s::VARCHAR) RETURNING posts.id
#  {'title': 'test', 'content': 'test content'}
```

- update
```
post = db.get(Post, 1)      # 먼저 꺼내고
post.title = 'new title'    # 속성만 바꾸면
db.commit()                 # commit 때 바뀐 컬럼만 UPDATE

=> UPDATE posts SET title=%(title)s::VARCHAR WHERE posts.id = %(posts_id)s::INTEGER
```

- delete
```
post = db.get(Post, 1)
db.delete(post)
db.commit()

=> DELETE FROM posts WHERE posts.id = %(id)s::INTEGER
```

- 정리

| CRUD | ORM | SQL |
|---|---|---|
| C | `db.add(Post(...))` | `INSERT INTO posts ...` |
| R (전체) | `db.scalars(select(Post)).all()` | `SELECT * FROM posts` |
| R (하나) | `db.get(Post, id)` | `SELECT ... WHERE id = ?` |
| U | 객체 속성 변경 | `UPDATE posts SET ... WHERE id = ?` |
| D | `db.delete(post)` | `DELETE FROM posts WHERE id = ?` |

- `commit()`을 해야 실제로 DB에 저장됨 (안 하면 with문 끝날 때 ROLLBACK)
- update / delete는 ORM이 `WHERE id = ...`를 자동으로 붙여 줌 (SQL로 직접 쓸 땐 WHERE 빠뜨리면 전체가 바뀜)

