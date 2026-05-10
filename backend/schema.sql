-- Jewelry store schema (MySQL 8+)
-- Note: this file does not CREATE DATABASE / USE — the seed script
-- creates the database (when permissions allow) and connects to it
-- before applying this schema. Keeps the file portable to managed
-- MySQL services that don't grant CREATE DATABASE.

-- ----------------------------------------------------------------------------
-- Users
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
  id              INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  name            VARCHAR(100) NOT NULL,
  email           VARCHAR(150) NOT NULL UNIQUE,
  password_hash   VARCHAR(255) NOT NULL,
  phone           VARCHAR(20)  DEFAULT NULL,
  role            ENUM('user','admin') NOT NULL DEFAULT 'user',
  created_at      TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at      TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP
                                ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_users_role (role)
) ENGINE=InnoDB;

-- ----------------------------------------------------------------------------
-- Products
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS products (
  id              INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  name            VARCHAR(200) NOT NULL,
  description     TEXT,
  price           DECIMAL(10,2) NOT NULL,
  category        VARCHAR(80)  NOT NULL,
  material        VARCHAR(80)  DEFAULT NULL,
  stock           INT UNSIGNED NOT NULL DEFAULT 0,
  image_url       VARCHAR(500) DEFAULT NULL,
  created_at      TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at      TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP
                                ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_products_category (category),
  INDEX idx_products_price    (price),
  FULLTEXT KEY ft_products_name_desc (name, description)
) ENGINE=InnoDB;

-- ----------------------------------------------------------------------------
-- Orders
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS orders (
  id              INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  user_id         INT UNSIGNED NOT NULL,
  total           DECIMAL(10,2) NOT NULL,
  status          ENUM('pending','processing','shipped','delivered','cancelled')
                  NOT NULL DEFAULT 'pending',
  address         VARCHAR(500) NOT NULL,
  phone           VARCHAR(20)  NOT NULL,
  payment_method  ENUM('cod','card','upi') NOT NULL DEFAULT 'cod',
  created_at      TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at      TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP
                                ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_orders_user   (user_id),
  INDEX idx_orders_status (status),
  CONSTRAINT fk_orders_user FOREIGN KEY (user_id)
    REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ----------------------------------------------------------------------------
-- Order items
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS order_items (
  id              INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  order_id        INT UNSIGNED NOT NULL,
  product_id      INT UNSIGNED NOT NULL,
  product_name    VARCHAR(200) NOT NULL,
  quantity        INT UNSIGNED NOT NULL,
  unit_price      DECIMAL(10,2) NOT NULL,
  INDEX idx_oi_order   (order_id),
  INDEX idx_oi_product (product_id),
  CONSTRAINT fk_oi_order FOREIGN KEY (order_id)
    REFERENCES orders(id) ON DELETE CASCADE,
  CONSTRAINT fk_oi_product FOREIGN KEY (product_id)
    REFERENCES products(id) ON DELETE RESTRICT
) ENGINE=InnoDB;

-- ----------------------------------------------------------------------------
-- Reviews
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS reviews (
  id              INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  user_id         INT UNSIGNED NOT NULL,
  product_id      INT UNSIGNED NOT NULL,
  rating          TINYINT UNSIGNED NOT NULL,
  comment         TEXT,
  created_at      TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at      TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP
                                ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY uniq_user_product (user_id, product_id),
  INDEX idx_reviews_product (product_id),
  CONSTRAINT chk_rating CHECK (rating BETWEEN 1 AND 5),
  CONSTRAINT fk_reviews_user FOREIGN KEY (user_id)
    REFERENCES users(id) ON DELETE CASCADE,
  CONSTRAINT fk_reviews_product FOREIGN KEY (product_id)
    REFERENCES products(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ----------------------------------------------------------------------------
-- Expenses (admin tracker)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS expenses (
  id              INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  expense_type    VARCHAR(80)  NOT NULL,
  amount          DECIMAL(10,2) NOT NULL,
  expense_date    DATE         NOT NULL,
  note            VARCHAR(500) DEFAULT NULL,
  created_at      TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_expense_date (expense_date),
  INDEX idx_expense_type (expense_type)
) ENGINE=InnoDB;
