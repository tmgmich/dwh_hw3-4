CREATE TABLE "manufacturers" (
  "manufacturer_id" SERIAL PRIMARY KEY,
  "manufacturer_name" VARCHAR(100) NOT NULL
);


CREATE TABLE "products" (
  "category_id" BIGINT,
  "manufacturer_id" BIGINT,
  "product_id" SERIAL PRIMARY KEY,
  "pruduct_name" VARCHAR(255) NOT NULL
);

CREATE TABLE "categories" (
  "category_id" SERIAL PRIMARY KEY,
  "category_name" VARCHAR(100) NOT NULL
);

CREATE TABLE "price_change" (
  "product_id" BIGINT NOT NULL,
  "price_change_ts" TIMESTAMP NOT NULL,
  "new_price" NUMERIC(9, 2) NOT NULL,
  CONSTRAINT "product_pk" primary key ("product_id")
);

CREATE TABLE "deliveries" (
  "store_id" BIGINT,
  "product_id" BIGINT NOT NULL,
  "delivery_date" DATE NOT NULL,
  "product_count" INTEGER not null,
  constraint "product_pk" foreign key ("product_id") references "price_change" ("product_id")
);

CREATE TABLE "purchases" (
  "store_id" BIGINT NOT NULL,
  "customer_id" BIGINT NOT NULL,
  "purchase_id" SERIAL PRIMARY KEY,
  "purchase_date" TIMESTAMP NOT NULL
);

CREATE TABLE "stores" (
  "store_id" SERIAL PRIMARY KEY,
  "store_name" VARCHAR(255) NOT NULL
);

CREATE TABLE "customers" (
  "customer_id" SERIAL PRIMARY KEY,
  "store_name" VARCHAR(255) NOT NULL
);

CREATE TABLE "purchase_items" (
  "product_id" BIGINT NOT NULL,
  "purchase_id" BIGINT NOT NULL,
  "product_count" BIGINT NOT NULL,
  "product_price" NUMERIC(9,2) NOT NULL
);

ALTER TABLE "products" ADD FOREIGN KEY ("category_id") REFERENCES "categories" ("category_id");
ALTER TABLE "products" ADD FOREIGN KEY ("manufacturer_id") REFERENCES "manufacturers" ("manufacturer_id");

ALTER TABLE "purchase_items" ADD FOREIGN KEY ("product_id") REFERENCES "products" ("product_id");
ALTER TABLE "purchase_items" ADD FOREIGN KEY ("purchase_id") REFERENCES "purchases" ("purchase_id");

ALTER TABLE "deliveries" ADD FOREIGN KEY ("store_id") REFERENCES "stores" ("store_id");

ALTER TABLE "purchases" ADD FOREIGN KEY ("store_id") REFERENCES "stores" ("store_id");
ALTER TABLE "purchases" ADD FOREIGN KEY ("customer_id") REFERENCES "customers" ("customer_id");

CREATE SCHEMA IF NOT EXISTS presentation;








