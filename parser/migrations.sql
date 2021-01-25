CREATE DATABASE "youla"
  WITH OWNER "postgres"
  ENCODING 'UTF8'
  LC_COLLATE = 'ru_RU.UTF-8'
  LC_CTYPE = 'ru_RU.UTF-8'
  TEMPLATE = template0;


CREATE TABLE json_auth (
  id bigserial NOT NULL,
  status smallint NOT NULL DEFAULT 1,
  row jsonb,
  uses smallint,
  CONSTRAINT json_auth_id_pkey PRIMARY KEY (id)
);
