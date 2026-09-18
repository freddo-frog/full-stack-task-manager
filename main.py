#=== DATA ===
import sqlite3
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pydantic import BaseModel

DB_NAME = "tasks.db"

#=== functions ===
def get_connection():
    return sqlite3.connect(DB_NAME) #changed to sqlite3

def create_table():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS todos (" \
        "id INTEGER PRIMARY KEY AUTOINCREMENT, task TEXT NOT NULL, completed BOOLEAN DEFAULT FALSE, due_date DATE, priority INTEGER, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, category TEXT);")
    conn.commit()
    conn.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_table()

    yield

    #no shutdown logic needed here.
app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class Task(BaseModel):
    task: str
    due_date: str
    created_at: str
    priority: int | None = None
    category: str | None = None

@app.get("/view-tasks")
def view_tasks():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM todos;")
    rows = cur.fetchall()

    conn.close()
    return rows

@app.post("/add-task") #post is for creating new data
def add_task(new_task: Task):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO todos (task, due_date, created_at, priority, category) VALUES(?, ?, ?, ?, ?)", (new_task.task, new_task.due_date, new_task.created_at, new_task.priority, new_task.category))

    conn.commit()
    conn.close()

@app.patch("/complete-task/{task_ID}") #patch is for a partial update
def complete_task(task_ID):
    conn = get_connection()

    cur = conn.cursor()
    cur.execute(("UPDATE todos SET completed = true WHERE id = ?"), (task_ID,)) #needs a trailing comma otherwise python does not register as a tuple

    conn.commit()
    conn.close()

@app.delete("/delete-task/{removed_ID}") #delete is the wrapper for removing data
def remove_task(removed_ID):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(("DELETE FROM todos WHERE id = ?"), (removed_ID,))

    conn.commit()
    conn.close()
