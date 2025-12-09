import tkinter as tk
from tkinter import ttk, messagebox
import pyodbc
from datetime import datetime



def validate_input(name, age, phone):
    """Selection and iteration structures for validation"""
    errors = []
    
    
    if not name or len(name) < 2:
        errors.append("Name must be at least 2 characters")
    
    
    if not age.isdigit():
        errors.append("Age must be a number")
    elif int(age) < 10 or int(age) > 100:
        errors.append("Age must be between 10 and 100")
    
    
    digit_count = sum(1 for c in phone if c.isdigit())
    if digit_count < 10:
        errors.append("Phone must have at least 10 digits")
    
    return errors



class Member:
    """Member class representing a gym member"""
    
    def __init__(self, member_id, name, age, phone, membership_type, join_date=None):
        self.member_id = member_id
        self.name = name
        self.age = age
        self.phone = phone
        self.membership_type = membership_type
        self.join_date = join_date or datetime.now().strftime("%Y-%m-%d")
    
    def get_info(self):
        return f"{self.name} - {self.membership_type} - Age: {self.age}"
    
    def calculate_fee(self):
        fees = {
            "Basic": 1000,
            "Standard": 2000,
            "Premium": 3500
        }
        return fees.get(self.membership_type, 0)


class Trainer:
    """Trainer class"""
    
    def __init__(self, trainer_id, name, specialization):
        self.trainer_id = trainer_id
        self.name = name
        self.specialization = specialization
    
    def get_info(self):
        return f"{self.name} - {self.specialization}"



class DatabaseError(Exception):
    pass

class ValidationError(Exception):
    pass



SQL_SERVER = "DESKTOP-M1HTQTV"
DB_NAME = "GymDB"
CONN_STR_TEMPLATE = (
    "DRIVER={SQL Server};"
    f"SERVER={SQL_SERVER};"
    "Trusted_Connection=yes;"
)

class Database:
    
    
    def __init__(self, db_name=DB_NAME):
        self.db_name = db_name
        try:
        
            self.ensure_database_exists()
            self.create_tables()
        except pyodbc.Error as e:
            raise DatabaseError(f"Database initialization failed: {e}")
    
    def get_connection(self, use_db=True):
        
        try:
            if use_db:
                conn_str = CONN_STR_TEMPLATE + f"DATABASE={self.db_name};"
            else:
                conn_str = CONN_STR_TEMPLATE + "DATABASE=master;"
            conn = pyodbc.connect(conn_str, autocommit=False)
            return conn
        except pyodbc.Error as e:
            raise DatabaseError(f"Failed to connect to SQL Server: {e}")
    
    def ensure_database_exists(self):
        
        try:
        
            conn_str = CONN_STR_TEMPLATE + "DATABASE=master;"
            conn = pyodbc.connect(conn_str, autocommit=True)
            cur = conn.cursor()

            cur.execute("SELECT database_id FROM sys.databases WHERE Name = ?", (self.db_name,))
            row = cur.fetchone()
            if not row:
                cur.execute(f"CREATE DATABASE [{self.db_name}]")
                

            cur.close()
            conn.close()
        except pyodbc.Error as e:
            raise DatabaseError(f"Failed to ensure database exists: {e}")

    
    def create_tables(self):
        
        try:
            conn = self.get_connection(use_db=True)
            cur = conn.cursor()
            
        
            cur.execute("""
                IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[members]') AND type in (N'U'))
                CREATE TABLE dbo.members (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    name NVARCHAR(200) NOT NULL,
                    age INT NOT NULL,
                    phone NVARCHAR(50) NOT NULL,
                    membership_type NVARCHAR(50) NOT NULL,
                    join_date DATE NOT NULL
                );
            """)
            
            
            cur.execute("""
                IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[trainers]') AND type in (N'U'))
                CREATE TABLE dbo.trainers (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    name NVARCHAR(200) NOT NULL,
                    specialization NVARCHAR(200) NOT NULL
                );
            """)
            
            conn.commit()
            cur.close()
            conn.close()
        except pyodbc.Error as e:
            raise DatabaseError(f"Table creation failed: {e}")
    
    def add_member(self, member):
        
        try:
            conn = self.get_connection(use_db=True)
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO dbo.members (name, age, phone, membership_type, join_date)
                VALUES (?, ?, ?, ?, ?);
            """, (member.name, member.age, member.phone, member.membership_type, member.join_date))
            
            cur.execute("SELECT SCOPE_IDENTITY();")
            row = cur.fetchone()
            conn.commit()
            new_id = int(row[0]) if row and row[0] is not None else None
            cur.close()
            conn.close()
            return new_id
        except pyodbc.Error as e:
            raise DatabaseError(f"Failed to add member: {e}")
    
    def get_all_members(self):
        """Return all members as a list of tuples"""
        try:
            conn = self.get_connection(use_db=True)
            cur = conn.cursor()
            cur.execute("SELECT id, name, age, phone, membership_type, CONVERT(varchar(10), join_date, 120) FROM dbo.members ORDER BY id;")
            rows = cur.fetchall()
            cur.close()
            conn.close()
            # Convert pyodbc.Row to plain tuples for Treeview
            return [tuple(r) for r in rows]
        except pyodbc.Error as e:
            raise DatabaseError(f"Failed to retrieve members: {e}")
    
    def delete_member(self, member_id):
        try:
            conn = self.get_connection(use_db=True)
            cur = conn.cursor()
            cur.execute("DELETE FROM dbo.members WHERE id = ?;", (member_id,))
            conn.commit()
            cur.close()
            conn.close()
        except pyodbc.Error as e:
            raise DatabaseError(f"Failed to delete member: {e}")
    
    def search_members(self, search_term):
        try:
            conn = self.get_connection(use_db=True)
            cur = conn.cursor()
            like_term = f"%{search_term}%"
            cur.execute("""
                SELECT id, name, age, phone, membership_type, CONVERT(varchar(10), join_date, 120)
                FROM dbo.members
                WHERE name LIKE ?
                ORDER BY id;
            """, (like_term,))
            rows = cur.fetchall()
            cur.close()
            conn.close()
            return [tuple(r) for r in rows]
        except pyodbc.Error as e:
            raise DatabaseError(f"Search failed: {e}")




class GymManagementGUI:
    
    def __init__(self, root):
        self.root = root
        self.root.title("Gym Management System")
        self.root.geometry("900x600")
        
        try:
            self.db = Database()
        except DatabaseError as e:
            messagebox.showerror("DB Error", str(e))
            exit()
        
        self.setup_gui()
        self.load_members()
    
    def setup_gui(self):
        # Title
        tk.Label(self.root, text="Gym Management System",
                font=("Arial", 22, "bold"), bg="#1642a9", fg="white",
                pady=10).pack(fill=tk.X)
        
        main_frame = tk.Frame(self.root, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # -------- Left side form --------
        left = tk.LabelFrame(main_frame, text="Add New Member",
                            font=("Arial", 12, "bold"), padx=15, pady=15)
        left.pack(side=tk.LEFT, fill=tk.BOTH)
        
        # Name
        tk.Label(left, text="Name:", font=("Arial", 10)).grid(row=0, column=0, sticky="w")
        self.name_entry = tk.Entry(left, width=25)
        self.name_entry.grid(row=0, column=1, pady=5)
        
        # Age
        tk.Label(left, text="Age:", font=("Arial", 10)).grid(row=1, column=0, sticky="w")
        self.age_entry = tk.Entry(left, width=25)
        self.age_entry.grid(row=1, column=1, pady=5)
        
        # Phone
        tk.Label(left, text="Phone:", font=("Arial", 10)).grid(row=2, column=0, sticky="w")
        self.phone_entry = tk.Entry(left, width=25)
        self.phone_entry.grid(row=2, column=1, pady=5)
        
        # Membership
        tk.Label(left, text="Membership:", font=("Arial", 10)).grid(row=3, column=0, sticky="w")
        self.membership_var = tk.StringVar(value="Basic")
        self.membership_combo = ttk.Combobox(left, values=["Basic", "Standard", "Premium"],
                                        textvariable=self.membership_var, state="readonly", width=22)
        self.membership_combo.grid(row=3, column=1, pady=5)
        self.membership_combo.bind("<<ComboboxSelected>>", self.update_fee)
        
        # Buttons
        btn_frame = tk.Frame(left)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=15)
        
        tk.Button(btn_frame, text="Add Member", bg="#27ae60", fg="white",
                command=self.add_member, pady=5).pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_frame, text="Clear", bg="#7f8c8d", fg="white",
                command=self.clear_form, pady=5).pack(side=tk.LEFT, padx=5)
        
        # Fee label
        self.fee_label = tk.Label(left, text="Monthly Fee: Rs. 1000",
                                font=("Arial", 11, "bold"), fg="#e74c3c")
        self.fee_label.grid(row=5, column=0, columnspan=2, pady=10)
        
        # -------- Right side table --------
        right = tk.LabelFrame(main_frame, text="Members",
                            font=("Arial", 12, "bold"), padx=15, pady=15)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Search
        s_frame = tk.Frame(right)
        s_frame.pack(fill=tk.X)
        tk.Label(s_frame, text="Search:").pack(side=tk.LEFT)
        self.search_entry = tk.Entry(s_frame, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_entry.bind("<KeyRelease>", self.search_members)
        
        # Treeview
        tree_frame = tk.Frame(right)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.tree = ttk.Treeview(tree_frame,
                                columns=("ID", "Name", "Age", "Phone", "Type", "Date"),
                                show="headings", yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.tree.yview)
        
        for col, w in zip(("ID","Name","Age","Phone","Type","Date"),
                        (40,120,40,100,80,100)):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=w)
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        tk.Button(right, text="Delete Selected", bg="#c0392b", fg="white",
                command=self.delete_member, pady=5).pack(pady=10)
    

    
    def add_member(self):
        name = self.name_entry.get().strip()
        age = self.age_entry.get().strip()
        phone = self.phone_entry.get().strip()
        membership = self.membership_var.get()
        
        try:
            errors = validate_input(name, age, phone)
            if errors:
                raise ValidationError("\n".join(errors))
            
            member = Member(None, name, int(age), phone, membership)
            member_id = self.db.add_member(member)
            member.member_id = member_id
            
            self.load_members()
            self.clear_form()
            
            messagebox.showinfo("Success", f"Member added!\nFee: Rs. {member.calculate_fee()}")
        
        except ValidationError as e:
            messagebox.showerror("Validation Error", str(e))
        except DatabaseError as e:
            messagebox.showerror("Database Error", str(e))
    
    def delete_member(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Select a member to delete")
            return
        
        item = self.tree.item(selected[0])
        member_id = item["values"][0]
        
        if messagebox.askyesno("Confirm", "Delete this member?"):
            self.db.delete_member(member_id)
            self.load_members()
    
    def search_members(self, event=None):
        text = self.search_entry.get().strip()
        if text == "":
            self.load_members()
            return
        
        members = self.db.search_members(text)
        self.display_members(members)
    
    def update_fee(self, event=None):
        fees = {"Basic": 1000, "Standard": 2000, "Premium": 3500}
        fee = fees.get(self.membership_var.get(), 1000)
        self.fee_label.config(text=f"Monthly Fee: Rs. {fee}")
    
    
    
    def clear_form(self):
        self.name_entry.delete(0, tk.END)
        self.age_entry.delete(0, tk.END)
        self.phone_entry.delete(0, tk.END)
        self.membership_var.set("Basic")
        self.update_fee()
    
    def load_members(self):
        members = self.db.get_all_members()
        self.display_members(members)
    
    def display_members(self, members):
        self.tree.delete(*self.tree.get_children())
        for m in members:
            self.tree.insert("", tk.END, values=m)


if __name__ == "__main__":
    root = tk.Tk()
    app = GymManagementGUI(root)
    root.mainloop()
