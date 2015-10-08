--test tables
    create VIEW "feedslabels" (
        "id" int4,
        "title" varchar(512),
        "link" varchar(255),
        "description" varchar(255),
        "homepage" text(2147483647),
        "icon" bytea,
        "unread_count" int4,
        "add_date" timestamptz,
        "active_flag" bool,
        "label" varchar(2147483647)
    );

    create TABLE "test_insert_articles" (
        "id" bigserial not null default nextval('test_insert_articles_id_seq'::regclass),
        "feed_id" int4 not null,
        "link" text(2147483647),
        "title" varchar(2147483647),
        "content" text(2147483647),
        "viewed_flag" bool,
        "read_later_flag" bool,
        "add_date" timestamptz not null default now(),
        "update_date" timestamptz not null default now(),
        "rating_int" int2,
        "rating_enum" rating(2147483647),
        "publish_date" timestamp
    );
    CREATE UNIQUE INDEX "uq_article" ON "test_insert_articles" ("feed_id", "link", "title");

--prod DDL
    create TABLE "articles" (
        "id" bigserial not null default nextval('articles_id_seq'::regclass),
        "feed_id" int4 not null,
        "link" text(2147483647),
        "title" varchar(2147483647),
        "content" text(2147483647),
        "viewed_flag" bool,
        "read_later_flag" bool,
        "add_date" timestamptz not null default now(),
        "update_date" timestamptz not null default now(),
        "rating_int" int2,
        "rating_enum" rating(2147483647),
        "publish_date" timestamp,
        PRIMARY KEY ("id"),
        FOREIGN KEY ("feed_id") REFERENCES "feeds" ("id"),
        FOREIGN KEY ("feed_id") REFERENCES "feeds" ("id")
    );
    CREATE UNIQUE INDEX "article_id_index" ON "articles" ("id");
    CREATE UNIQUE INDEX "article_feed_id_index" ON "articles" ("feed_id");

    create TABLE "feeds" (
        "id" serial not null default nextval('feeds_id_seq'::regclass),
        "title" varchar(512),
        "link" varchar(255),
        "labels" _varchar,
        "description" varchar(255),
        "homepage" text(2147483647),
        "icon" bytea,
        "unread_count" int4,
        "add_date" timestamptz not null,
        "active_flag" bool,
        "update_date" timestamptz not null
        PRIMARY KEY ("id")
    );
    CREATE UNIQUE INDEX "id_index" ON "feeds" ("id");
    CREATE UNIQUE INDEX "unique_link" ON "feeds" ("link");