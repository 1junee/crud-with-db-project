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
uv init crud_with_db -bare --python 3.14
```


```
uv add "fastapi[standard]" sqlalchemy "
psycopg[binary]"
```