const express = require("express");
const sqlite3 = require("sqlite3").verbose();
const { v4: uuidv4 } = require("uuid");
const bcrypt = require("bcrypt");

const app = express();
const port = 3000;

app.use(express.json());

// Initialize the SQLite database
const db = new sqlite3.Database("./users.db", (err) => {
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
app.post("/login", async (req, res) => {
  const { action ,user, pass } = req.body;

  if (action === "register") {
    // Check if the username already exists
    db.get("SELECT * FROM users WHERE username = ?", [user], async (err, row) => {
      if (err) {
        res.status(500).json({ error: "Database error" });
      } else if (row) {
        res.status(400).json({ error: "Username already exists" });
      } else {
        // Hash the password
        const hashedPassword = await bcrypt.hash(pass, 10);
        const id = uuidv4();

        db.run("INSERT INTO users (id, username, password) VALUES (?, ?, ?)", [id, user, hashedPassword], (err) => {
          if (err) {
            res.status(500).json({ error: "Database error" });
          } else {
            console.log("Registerd :"+row.id);
            res.json({ UUID:id,username:user });
          }
        });
      }
    });
  } else if (action === "login") {
    // Get the stored hash for the username
    db.get("SELECT id, password FROM users WHERE username = ?", [user], async (err, row) => {
      if (err) {
        res.status(500).json({ error: "Database error" });
      } else if (row) {
        // Compare the hashed password
        const match = await bcrypt.compare(pass, row.password);
        if (match) {
          console.log("Logged in :"+row.id);
          res.json({ UUID: row.id,username:user });
        } else {
          res.status(400).json({ error: "Invalid username or password" });
        }
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
