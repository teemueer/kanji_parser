create table if not exists codepoints (
    uni     int primary key,
    sjis    int,
    jis     int,
    euc     int,
    ku      int,
    ten     int
);

create table if not exists kanji (
    uni         int primary key,
    kanji       text,
    
    radical     int,
    radical_c   int,
    parts       text,
    grade       int,
    
    nelson      int,
    heisig      int,
    heisig6     int,
    henshall    int,
    halpern     int,
    halpern_k   int,
    halpern_k2  int
);

create table if not exists meanings (
    id      integer primary key autoincrement,
    uni     int,
    meaning text
);

create table if not exists onyomi (
    id      integer primary key autoincrement,
    uni     int,
    onyomi  text
);

create table if not exists kunyomi (
    id      integer primary key autoincrement,
    uni     int,
    kunyomi text
);

create table if not exists words (
    id      integer primary key autoincrement,
    word    text,
    reading text,
    meaning text
)