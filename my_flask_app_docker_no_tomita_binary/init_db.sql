-- Табла нграм
CREATE TABLE "Ngram" (
    "IDWord" SERIAL NOT NULL,
    "Word" CHARACTER(254),
    "IDText" INTEGER NOT NULL,
    PRIMARY KEY ("IDWord", "IDText")
);

-- Табла лем
CREATE TABLE "Lem" (
    "IDLem" SERIAL NOT NULL,
    "Lem" CHARACTER(254),
    "PoS" CHARACTER(254),
    "IDWord" INTEGER NOT NULL,
    "IDText" INTEGER NOT NULL,
    PRIMARY KEY ("IDLem", "IDWord", "IDText")
);

-- Табла для текстов
CREATE TABLE "Text" (
    "IDText" SERIAL NOT NULL,
    "Text" TEXT,
    PRIMARY KEY ("IDText")
);

-- Отдельная табла для словосочетаний (в оригинальном коде от АА не было,  но она кажись нужна)
CREATE TABLE "Phrases" (
    "IDPhrase" SERIAL NOT NULL,
    "IDText" INTEGER NOT NULL,
    "Phrase" CHARACTER(254),
    PRIMARY KEY ("IDPhrase"),
    FOREIGN KEY ("IDText") REFERENCES "Text"("IDText") ON UPDATE NO ACTION ON DELETE CASCADE
);

-- отношения FK
ALTER TABLE "Ngram" ADD CONSTRAINT "textGram" FOREIGN KEY ("IDText")
REFERENCES "Text" ("IDText") ON UPDATE NO ACTION ON DELETE CASCADE;

ALTER TABLE "Lem" ADD CONSTRAINT "NgrLem" FOREIGN KEY ("IDWord", "IDText")
REFERENCES "Ngram" ("IDWord", "IDText") ON UPDATE NO ACTION ON DELETE CASCADE;
