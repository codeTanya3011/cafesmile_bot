# ☕ CafeSmile Telegram Bot

An interactive Telegram bot for café order automation, featuring integrated payment systems and real-time merchant notifications.

## 🔗 Try it on Telegram
**[@cafesmile68_bot](https://t.me/cafesmile68_bot)**

---

## 🛠 About The Project
This bot is a comprehensive **MVP (Minimum Viable Product)** for an order automation system. It guides the client from browsing the menu to the final payment and transfers order details directly to the kitchen.

### Key Features for Users:
* **Interactive Menu**: User-friendly navigation through dish categories with photos and descriptions.
* **Smart Shopping Cart**: Dynamic quantity adjustment (via `+` / `-` buttons) with instant total price updates—no interface reloads required.
* **Automated Calculations**: The bot automatically calculates the subtotal and adds the delivery fee based on the selected type (Courier or Pickup).
* **Online Payments**: Full integration with **Telegram Payments** (supporting Apple Pay, Google Pay, and standard bank cards).

### Business Features (Administration):
* **Merchant Reports**: Instant delivery of detailed order reports (cart content, total amount, and customer contact info).
* **Database Management**: Persistence of user history, active carts, and orders using **PostgreSQL**, with the ability for users to view their history. 
* **Scalability**: Designed with a structure that allows adding general business statistics and analytics in future production releases.

---

## ⚙️ Tech Stack
The project is built on a modern Python development stack:
* **Framework**: [Aiogram 3.x](https://docs.aiogram.dev/) — A powerful asynchronous library for the Telegram Bot API.
* **Database**: **PostgreSQL** — A reliable relational database.
* **ORM**: **SQLAlchemy 2.0** — Database interaction in full asynchronous mode.
* **Containerization**: **Docker & Docker Compose** — For stable deployment and service isolation.

---

## 💳 Testing the Payment System (Instructions)
Since the bot operates in test mode, you can simulate an online payment using the following data:
* **Card Number**: `4444 3333 2222 1111`
* **CVC**: `123` (or any 3 digits)
* **Expiry Date**: Any future date (e.g., `12/29`)

---

## 📂 Project Structure
* `handlers/` — Core logic for command processing, checkout flow, and payment handling.
* `database/` — Asynchronous SQLAlchemy models and database interaction methods.
* `keyboards/` — Generators for dynamic inline and reply keyboards.
* `utils/` — Utility modules and tools:
    * **States**: FSM (Finite State Machine) definitions for checkout logic (delivery selection, geolocation, payment methods).
    * **Captions**: Centralized storage for text templates and bot responses (maintaining Clean Code by avoiding hardcoded strings).
    * **Calculations**: Helper functions for order subtotals and logistics verification.
* `docker-compose.yml` — Container orchestration for the bot and database for rapid deployment.

