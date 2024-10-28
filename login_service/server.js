const express = require("express");
const sqlite3 = require("sqlite3").verbose();
const { v4: uuidv4 } = require("uuid");

const app = express();
const port = 3000;

app.use(express.json());

// Initialize the SQLite database
const db = new sqlite3.Database(":memory:", (err) => {
  if (err) {
    console.error("Could not open database:", err);
  } else {
    console.log("Connected to the SQLite database in-memory.");
  }
});

// Create users table if not exists
db.serialize(() => {
  db.run(`
    CREATE TABLE IF NOT EXISTS users (
      id TEXT PRIMARY KEY,
      username TEXT UNIQUE,
      password TEXT
    )
  `);
});

// Register or login route
app.post("/login", (req, res) => {
    console.log("got response");
  const { user, pass, action } = req.body;

  if (action === "register") {
    // Register action
    db.get("SELECT * FROM users WHERE username = ?", [user], (err, row) => {
      if (err) {
        res.status(500).json({ error: "Database error" });
      } else if (row) {
        res.status(400).json({ error: "Username already exists" });
      } else {
        const id = uuidv4();
        db.run("INSERT INTO users (id, username, password) VALUES (?, ?, ?)", [id, user, pass], (err) => {
          if (err) {
            res.status(500).json({ error: "Database error" });
          } else {
            res.json({ id });
          }
        });
      }
    });
  } else if (action === "login") {
    // Login action
    db.get("SELECT id FROM users WHERE username = ? AND password = ?", [user, pass], (err, row) => {
      if (err) {
        res.status(500).json({ error: "Database error" });
      } else if (row) {
        res.json({ id: row.id });
      } else {
        res.status(400).json({ error: "Invalid username or password" });
      }
    });
  } else {
    res.status(400).json({ error: "Invalid action" });
  }
});

// Start the server
app.listen(port, () => {
  console.log(`Server running on http://localhost:${port}`);
});
