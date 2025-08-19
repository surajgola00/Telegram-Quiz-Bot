# 📚 QuizziBot - Telegram Quiz Bot  

A fun and interactive **Telegram Quiz Bot** built using **Python, Telebot, and MySQL**.  
It allows users to test their knowledge across multiple categories, track their scores, and compete with friends.  
Admins can upload new quiz questions, manage logs, and view users.  

👉 Try it here: [QuizziBot on Telegram](https://t.me/daily_quize_bot)  

---

## 🚀 Features  

- 🎉 **Quizzes in multiple categories** – users can pick topics and answer questions.  
- ✅ **Score tracking** – progress is saved for each category.  
- 🤖 **Interactive UI** – inline keyboards for answering, skipping, hints, and reporting questions.  
- 📝 **Admin tools** – view logs, clear errors, add new questions via JSON file uploads.  
- 🔔 **Friendly responses** – motivational messages for correct/incorrect answers.  
- 🧑‍💻 **Contact feature** – users can directly send issues or feedback to the admin.  

---

## 🔐 Admin Features & Advanced Commands  

Admins have access to additional commands and tools for managing the bot and users.  

### 👥 User Management  
- `/users` – View the **list of all users** connected with the bot.  
- Tap on a user from the list to **send them a personal message** directly through the bot.  
- User data (Telegram ID, username, and name) is stored securely in the database.  

### 📝 Question Management  
- Upload **JSON files** with questions to expand the quiz database.  
- If a user **reports a question** using the `Report🛑` button, the **reported question is automatically forwarded** to the admin with details (question, options, correct answer, and reporting user info).  
- Admins get alerts when users complete all questions in a category.  

### 📩 Communication Tools  
- `/contact` – Users can reach admins via the bot.  
- The bot forwards user messages (and even **pictures or documents**) directly to the admin’s chat.  
- Users can cancel the contact process anytime with `/cancel`.  

### 🛠️ Log & Database Tools  
- `/log` – View error logs with detailed messages and timestamps.  
- `/clear` – Clear all error logs.  
- `/dbcommand <SQL>` – Run custom SQL queries directly (⚠️ use carefully).  

---

## 👨‍💻 Admin Workflow Example  

1. A user selects `/contact` and sends an issue (text or photo).  
   → The bot forwards it to the admin.  
2. A user reports a question.  
   → The full question (with options and correct answer) is sent to the admin for review.  
3. The admin can use `/users` to see all connected users and **send them personal replies** if needed.  

---

## 🛠️ Tech Stack  

- **Python 3**  
- **PyTelegramBotAPI (telebot)** – Telegram Bot Framework  
- **Flask** – for handling webhooks  
- **MySQL** – stores users, questions, and scores  
- **JSON** – for uploading new quiz questions  

---

## 📂 Project Structure  

```
├── main.py           # Main bot logic & commands
├── database.py       # Database operations (users, scores, questions, logs)
├── details.py        # Bot token, admin ID, DB credentials (keep this secret!)
├── botmessages.py    # Predefined user-friendly messages
├── BotAccessLink.txt # Link to access the deployed bot
├── questions.json    # Sample quiz questions file
```

---

## ⚙️ Setup Instructions  

1. **Clone this repository**  
   ```bash
   git clone https://github.com/surajgola00/Telegram-Quiz-Bot
   cd Telegram-Quiz-Bot
   ```

2. **Install dependencies**  
   ```bash
   pip install pyTelegramBotAPI flask mysql-connector-python
   ```

3. **Configure `details.py`**  
   Fill in your own values:  
   ```python
   TOKEN = "your-telegram-bot-token"
   admin_id = 123456789
   secret = "yoursecret"
   url = "https://yourserver.com/" + secret

   config = {
     "host": "localhost",
     "user": "your_db_user",
     "password": "your_db_password",
     "database": "quizdb"
   }
   ```

4. **Setup MySQL Database**  
   ```sql
   CREATE DATABASE quizdb;
   USE quizdb;

   CREATE TABLE users (
       tg_id BIGINT PRIMARY KEY,
       user_name VARCHAR(255),
       name VARCHAR(255)
   );

   CREATE TABLE user_score (
       tg_id BIGINT PRIMARY KEY,
       -- Add one column per quiz category
       science INT DEFAULT 1,
       history INT DEFAULT 1
   );

   CREATE TABLE questions (
       id INT AUTO_INCREMENT PRIMARY KEY,
       category VARCHAR(255),
       q_no INT,
       q TEXT,
       ans VARCHAR(255),
       options TEXT,
       hint TEXT,
       info TEXT
   );

   CREATE TABLE error_logs (
       id INT AUTO_INCREMENT PRIMARY KEY,
       error_message TEXT,
       location VARCHAR(255),
       timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
   );
   ```

5. **Run the bot**  
   ```bash
   python main.py
   ```

---

## 📤 Adding New Questions  

- Prepare a JSON file in this format:  
   ```json
   [
     {
       "category": "science",
       "q": "What is the boiling point of water?",
       "ans": "100°C",
       "options": ["90°C", "100°C", "120°C", "80°C"],
       "hint": "It’s the standard temperature at sea level.",
       "info": "Water boils at 100°C under standard atmospheric pressure."
     }
   ]
   ```
- Send the file to the bot as **Admin**.  
- The bot will automatically add it to the database.  

📌 A **sample file is included** → [`questions.json`](questions.json).  

---

## 🤝 Contributing Guidelines  

Want to add new quiz questions or categories?  
1. Fork this repo 🍴  
2. Add your questions in a new **`questions.json`** file following the sample format.  
3. Submit a Pull Request ✅  

---

## 📸 Demo  

<img width="800" alt="quiz-demo" src="https://github.com/user-attachments/assets/6c35dc0f-7f66-4535-86a1-42fe65f1618c" />

---

## 👨‍💻 Author  

Developed by **Suraj Gola**  
Contributions & suggestions are welcome!  

---

## 🛡️ License  

This project is licensed under the **MIT License** – feel free to use, modify, and share.  
