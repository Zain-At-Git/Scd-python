import pyodbc
import tkinter as tk
from tkinter import messagebox, simpledialog

# ------------------- CONFIG -------------------
CONN_STR = (
    r"DRIVER={ODBC Driver 17 for SQL Server};"
    r"SERVER=DESKTOP-M1HTQTV;"     # change if needed
    r"DATABASE=master;"            # change to your DB
    r"Trusted_Connection=yes;"
)

def get_conn():
    try:
        return pyodbc.connect(CONN_STR)
    except Exception as e:
        messagebox.showerror("DB Error", f"Could not connect to database:\n{e}")
        return None

# ------------------- DB SETUP -------------------
def create_table():
    conn = get_conn()
    if not conn:
        return
    try:
        cursor = conn.cursor()
        cursor.execute("""
        IF OBJECT_ID('students', 'U') IS NULL
        BEGIN
            CREATE TABLE students(
                id INT IDENTITY(1,1) PRIMARY KEY,
                name NVARCHAR(50),
                age INT,
                grade NVARCHAR(10)
            )
        END
        """)
        conn.commit()
    except Exception as e:
        messagebox.showerror("DB Error", f"Error creating table:\n{e}")
    finally:
        conn.close()

def get_all_students():
    conn = get_conn()
    if not conn:
        return []
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, age, grade FROM students ORDER BY id")
        rows = cursor.fetchall()
        return rows
    except Exception as e:
        messagebox.showerror("DB Error", f"Could not fetch students:\n{e}")
        return []
    finally:
        conn.close()

# ------------------- CRUD FUNCTIONS -------------------
def add_student():
    name = name_entry.get().strip()
    age = age_entry.get().strip()
    grade = grade_entry.get().strip()

    if not name:
        messagebox.showwarning("Validation", "Name is required.")
        return

    conn = get_conn()
    if not conn:
        return
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO students (name, age, grade) VALUES (?, ?, ?)",
            (name, int(age) if age != "" else None, grade)
        )
        conn.commit()
        messagebox.showinfo("Success", "Student added.")
        clear_inputs()
    except ValueError:
        messagebox.showwarning("Validation", "Age must be a number (or leave blank).")
    except Exception as e:
        messagebox.showerror("DB Error", str(e))
    finally:
        conn.close()

def view_students():
    rows = get_all_students()
    view_win = tk.Toplevel(root)
    view_win.title("All Students")
    view_win.geometry("420x300")

    # Header
    header = tk.Label(view_win, text=f"{'ID':<6}{'Name':<25}{'Age':<8}{'Grade':<8}", anchor="w", font=("TkDefaultFont", 10, "bold"))
    header.pack(fill="x", padx=8, pady=(8,2))

    # Listbox
    listbox = tk.Listbox(view_win, font=("Courier", 10))
    listbox.pack(fill="both", expand=True, padx=8, pady=4)
    if not rows:
        listbox.insert(tk.END, "No students found.")
    else:
        for r in rows:
            id_, name, age, grade = r
            age_str = str(age) if age is not None else ""
            listbox.insert(tk.END, f"{id_:<6}{name:<25}{age_str:<8}{grade:<8}")

    # Close button
    tk.Button(view_win, text="Close", command=view_win.destroy).pack(pady=6)

def update_student():
    try:
        student_id = simpledialog.askinteger("Update Student", "Enter student ID to update:", parent=root, minvalue=1)
        if student_id is None:
            return
        name = name_entry.get().strip()
        age = age_entry.get().strip()
        grade = grade_entry.get().strip()
        if not name:
            messagebox.showwarning("Validation", "Name is required to update.")
            return

        conn = get_conn()
        if not conn:
            return
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(1) FROM students WHERE id = ?", (student_id,))
        exists = cursor.fetchone()[0]
        if not exists:
            messagebox.showwarning("Not found", f"No student with ID {student_id}")
            return

        cursor.execute(
            "UPDATE students SET name = ?, age = ?, grade = ? WHERE id = ?",
            (name, int(age) if age != "" else None, grade, student_id)
        )
        conn.commit()
        messagebox.showinfo("Success", f"Student ID {student_id} updated.")
        clear_inputs()
    except ValueError:
        messagebox.showwarning("Validation", "Age must be a number (or leave blank).")
    except Exception as e:
        messagebox.showerror("DB Error", str(e))
    finally:
        try:
            conn.close()
        except:
            pass

def delete_student():
    student_id = simpledialog.askinteger("Delete Student", "Enter student ID to delete:", parent=root, minvalue=1)
    if student_id is None:
        return

    if not messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete student ID {student_id}?"):
        return

    conn = get_conn()
    if not conn:
        return
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(1) FROM students WHERE id = ?", (student_id,))
        exists = cursor.fetchone()[0]
        if not exists:
            messagebox.showwarning("Not found", f"No student with ID {student_id}")
            return

        cursor.execute("DELETE FROM students WHERE id = ?", (student_id,))
        conn.commit()
        messagebox.showinfo("Deleted", f"Student ID {student_id} deleted.")
    except Exception as e:
        messagebox.showerror("DB Error", str(e))
    finally:
        conn.close()

# ------------------- UTIL -------------------
def clear_inputs():
    name_entry.delete(0, tk.END)
    age_entry.delete(0, tk.END)
    grade_entry.delete(0, tk.END)

# ------------------- GUI -------------------
create_table()

root = tk.Tk()
root.title("Student Entry GUI")
root.geometry("360x300")
root.resizable(False, False)

# Labels & entries
tk.Label(root, text="Name").pack(pady=(10,0))
name_entry = tk.Entry(root, width=30)
name_entry.pack()

tk.Label(root, text="Age").pack(pady=(8,0))
age_entry = tk.Entry(root, width=30)
age_entry.pack()

tk.Label(root, text="Grade").pack(pady=(8,0))
grade_entry = tk.Entry(root, width=30)
grade_entry.pack()

# Buttons row
btn_frame = tk.Frame(root)
btn_frame.pack(pady=14)

tk.Button(btn_frame, text="Add Student", width=14, command=add_student).grid(row=0, column=0, padx=6, pady=3)
tk.Button(btn_frame, text="View Students", width=14, command=view_students).grid(row=1, column=0, padx=6, pady=3)
tk.Button(btn_frame, text="Update Student", width=14, command=update_student).grid(row=0, column=1, padx=6, pady=3)
tk.Button(btn_frame, text="Delete Student", width=14, command=delete_student).grid(row=1, column=1, padx=6, pady=3)

# small help label
tk.Label(root, text="To update/delete provide the record ID when prompted.", fg="gray", wraplength=320).pack(pady=(6,4))

root.mainloop()
