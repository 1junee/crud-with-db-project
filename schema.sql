CREATE TABLE posts (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT NOT NULL
);

INSERT INTO posts (title, content) VALUES
('출석 인증', '안녕하세요, 출석 인증합니다.'),
('등업 신청', '안녕하세요, 등업 신청합니다.');

