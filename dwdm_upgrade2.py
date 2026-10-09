# ================================================================
# DWDM UPGRADE 2
# SMART STUDENT PERFORMANCE DATA WAREHOUSE
# AND DATA MINING SYSTEM
#
# Technologies:
# Tkinter     -> GUI
# SQLite      -> Data Warehouse
# Pandas      -> ETL / Data Processing
# NumPy       -> Numerical Processing
# Matplotlib  -> Visualization
# Scikit-learn-> Data Mining / ML
#
# Features:
# 1. Student Data Entry
# 2. CSV Import
# 3. ETL Processing
# 4. Star Schema Data Warehouse
# 5. OLAP Roll-up
# 6. OLAP Drill-down
# 7. OLAP Slice
# 8. OLAP Dice
# 9. Decision Tree
# 10. Random Forest
# 11. Feature Importance
# 12. K-Means Clustering
# 13. Performance Prediction
# 14. Multiple Charts
# 15. Data Warehouse Viewer
# 16. Star Schema Viewer
# 17. Export to CSV
# 18. Dashboard
# ================================================================

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn.ensemble import RandomForestClassifier
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report


# ================================================================
# DATABASE
# ================================================================

DB_NAME = "DWDM_Upgrade2_Warehouse.db"

conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

cursor.execute("PRAGMA foreign_keys = ON")


# ================================================================
# STAR SCHEMA
# ================================================================

cursor.executescript("""
CREATE TABLE IF NOT EXISTS dim_student (
    student_key INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT UNIQUE NOT NULL,
    student_name TEXT NOT NULL,
    gender TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS dim_department (
    department_key INTEGER PRIMARY KEY AUTOINCREMENT,
    department_name TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS dim_semester (
    semester_key INTEGER PRIMARY KEY AUTOINCREMENT,
    semester_number INTEGER UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS dim_time (
    time_key INTEGER PRIMARY KEY AUTOINCREMENT,
    academic_year TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS fact_performance (
    performance_key INTEGER PRIMARY KEY AUTOINCREMENT,

    student_key INTEGER NOT NULL,
    department_key INTEGER NOT NULL,
    semester_key INTEGER NOT NULL,
    time_key INTEGER NOT NULL,

    study_hours REAL NOT NULL,
    attendance REAL NOT NULL,
    assignment_score REAL NOT NULL,
    internal_marks REAL NOT NULL,
    exam_score REAL NOT NULL,

    performance TEXT NOT NULL,

    FOREIGN KEY(student_key)
        REFERENCES dim_student(student_key),

    FOREIGN KEY(department_key)
        REFERENCES dim_department(department_key),

    FOREIGN KEY(semester_key)
        REFERENCES dim_semester(semester_key),

    FOREIGN KEY(time_key)
        REFERENCES dim_time(time_key)
);
""")

conn.commit()


# ================================================================
# GUI COLORS
# ================================================================

NAVY = "#172554"
BLUE = "#2563eb"
CYAN = "#0891b2"
GREEN = "#16a34a"
PURPLE = "#7c3aed"
ORANGE = "#ea580c"
RED = "#dc2626"
TEAL = "#0f766e"
WHITE = "#ffffff"
LIGHT = "#f1f5f9"
DARK = "#1e293b"
GRAY = "#64748b"


# ================================================================
# MAIN WINDOW
# ================================================================

root = tk.Tk()

root.title(
    "DWDM Upgrade 2 - Smart Student Performance Data Warehouse"
)

root.geometry("1400x850")
root.minsize(1150, 700)
root.configure(bg=LIGHT)


# ================================================================
# UTILITY FUNCTIONS
# ================================================================

def calculate_performance(score):

    if score >= 75:
        return "Good"

    elif score >= 50:
        return "Average"

    else:
        return "Poor"


def validate_number(value, minimum, maximum, field_name):

    try:
        number = float(value)
    except ValueError:
        raise ValueError(
            f"{field_name} must be a valid number."
        )

    if number < minimum or number > maximum:

        raise ValueError(
            f"{field_name} must be between "
            f"{minimum} and {maximum}."
        )

    return number


def get_full_data():

    query = """

    SELECT

        f.performance_key,

        s.student_id,
        s.student_name,
        s.gender,

        d.department_name,

        sem.semester_number,

        t.academic_year,

        f.study_hours,
        f.attendance,
        f.assignment_score,
        f.internal_marks,
        f.exam_score,

        f.performance

    FROM fact_performance f

    JOIN dim_student s
        ON f.student_key = s.student_key

    JOIN dim_department d
        ON f.department_key = d.department_key

    JOIN dim_semester sem
        ON f.semester_key = sem.semester_key

    JOIN dim_time t
        ON f.time_key = t.time_key

    ORDER BY f.performance_key

    """

    return pd.read_sql_query(query, conn)


# ================================================================
# INSERT DATA INTO STAR SCHEMA
# ================================================================

def insert_record(
    student_id,
    student_name,
    gender,
    department,
    semester,
    academic_year,
    study_hours,
    attendance,
    assignment_score,
    internal_marks,
    exam_score
):

    student_id = str(student_id).strip()
    student_name = str(student_name).strip()
    department = str(department).strip()
    academic_year = str(academic_year).strip()

    if not student_id:
        raise ValueError("Student ID is required.")

    if not student_name:
        raise ValueError("Student Name is required.")

    if not department:
        raise ValueError("Department is required.")

    if not academic_year:
        raise ValueError("Academic Year is required.")

    try:
        semester = int(semester)
    except ValueError:
        raise ValueError("Semester must be an integer.")

    if semester < 1 or semester > 12:
        raise ValueError(
            "Semester must be between 1 and 12."
        )

    study_hours = validate_number(
        study_hours, 0, 24, "Study Hours"
    )

    attendance = validate_number(
        attendance, 0, 100, "Attendance"
    )

    assignment_score = validate_number(
        assignment_score, 0, 100, "Assignment Score"
    )

    internal_marks = validate_number(
        internal_marks, 0, 100, "Internal Marks"
    )

    exam_score = validate_number(
        exam_score, 0, 100, "Exam Score"
    )

    performance = calculate_performance(
        exam_score
    )

    # ------------------------------------------------------------
    # STUDENT DIMENSION
    # ------------------------------------------------------------

    cursor.execute(
        """
        SELECT student_key
        FROM dim_student
        WHERE student_id = ?
        """,
        (student_id,)
    )

    student = cursor.fetchone()

    if student:

        student_key = student[0]

        cursor.execute(
            """
            UPDATE dim_student
            SET student_name = ?,
                gender = ?
            WHERE student_key = ?
            """,
            (
                student_name,
                gender,
                student_key
            )
        )

    else:

        cursor.execute(
            """
            INSERT INTO dim_student
            (student_id, student_name, gender)
            VALUES (?, ?, ?)
            """,
            (
                student_id,
                student_name,
                gender
            )
        )

        student_key = cursor.lastrowid

    # ------------------------------------------------------------
    # DEPARTMENT DIMENSION
    # ------------------------------------------------------------

    cursor.execute(
        """
        INSERT OR IGNORE INTO dim_department
        (department_name)
        VALUES (?)
        """,
        (department,)
    )

    cursor.execute(
        """
        SELECT department_key
        FROM dim_department
        WHERE department_name = ?
        """,
        (department,)
    )

    department_key = cursor.fetchone()[0]

    # ------------------------------------------------------------
    # SEMESTER DIMENSION
    # ------------------------------------------------------------

    cursor.execute(
        """
        INSERT OR IGNORE INTO dim_semester
        (semester_number)
        VALUES (?)
        """,
        (semester,)
    )

    cursor.execute(
        """
        SELECT semester_key
        FROM dim_semester
        WHERE semester_number = ?
        """,
        (semester,)
    )

    semester_key = cursor.fetchone()[0]

    # ------------------------------------------------------------
    # TIME DIMENSION
    # ------------------------------------------------------------

    cursor.execute(
        """
        INSERT OR IGNORE INTO dim_time
        (academic_year)
        VALUES (?)
        """,
        (academic_year,)
    )

    cursor.execute(
        """
        SELECT time_key
        FROM dim_time
        WHERE academic_year = ?
        """,
        (academic_year,)
    )

    time_key = cursor.fetchone()[0]

    # ------------------------------------------------------------
    # FACT TABLE
    # ------------------------------------------------------------

    cursor.execute(
        """
        INSERT INTO fact_performance

        (
            student_key,
            department_key,
            semester_key,
            time_key,

            study_hours,
            attendance,
            assignment_score,
            internal_marks,
            exam_score,

            performance
        )

        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)

        """,

        (
            student_key,
            department_key,
            semester_key,
            time_key,

            study_hours,
            attendance,
            assignment_score,
            internal_marks,
            exam_score,

            performance
        )
    )

    conn.commit()


# ================================================================
# DASHBOARD VARIABLES
# ================================================================

total_records = tk.StringVar(value="0")
average_exam = tk.StringVar(value="0%")
average_attendance = tk.StringVar(value="0%")
good_students = tk.StringVar(value="0")
departments_count = tk.StringVar(value="0")


# ================================================================
# UPDATE DASHBOARD
# ================================================================

def update_dashboard():

    df = get_full_data()

    total_records.set(str(len(df)))

    if df.empty:

        average_exam.set("0%")
        average_attendance.set("0%")
        good_students.set("0")
        departments_count.set("0")

        return

    average_exam.set(
        f"{df['exam_score'].mean():.1f}%"
    )

    average_attendance.set(
        f"{df['attendance'].mean():.1f}%"
    )

    good_students.set(
        str(
            (df["performance"] == "Good").sum()
        )
    )

    departments_count.set(
        str(
            df["department_name"].nunique()
        )
    )


# ================================================================
# GENERIC TEXT WINDOW
# ================================================================

def create_text_window(
    title,
    text,
    width=1000,
    height=650
):

    window = tk.Toplevel(root)

    window.title(title)

    window.geometry(
        f"{width}x{height}"
    )

    window.configure(bg=WHITE)

    title_label = tk.Label(
        window,
        text=title,
        font=("Arial", 20, "bold"),
        bg=NAVY,
        fg=WHITE,
        pady=12
    )

    title_label.pack(fill="x")

    text_box = tk.Text(
        window,
        font=("Consolas", 11),
        wrap="none"
    )

    text_box.pack(
        fill="both",
        expand=True,
        padx=15,
        pady=15
    )

    text_box.insert(
        "1.0",
        text
    )

    text_box.config(
        state="disabled"
    )

    return window


# ================================================================
# ADD DATA WINDOW
# ================================================================

def add_data_window():

    window = tk.Toplevel(root)

    window.title(
        "Add Student Data"
    )

    window.geometry(
        "700x760"
    )

    window.configure(
        bg="#dbeafe"
    )

    tk.Label(
        window,
        text="ADD DATA TO DATA WAREHOUSE",
        font=("Arial", 20, "bold"),
        bg=BLUE,
        fg=WHITE,
        pady=14
    ).pack(fill="x")

    form = tk.Frame(
        window,
        bg="#dbeafe"
    )

    form.pack(
        pady=15
    )

    fields = [

        ("Student ID", ""),
        ("Student Name", ""),
        ("Department", ""),
        ("Semester", ""),
        ("Academic Year", "2026-27"),
        ("Study Hours / Day", ""),
        ("Attendance (%)", ""),
        ("Assignment Score", ""),
        ("Internal Marks", ""),
        ("Exam Score", "")
    ]

    entries = {}

    for row, (label, default) in enumerate(fields):

        tk.Label(
            form,
            text=label,
            font=("Arial", 11, "bold"),
            bg="#dbeafe"
        ).grid(
            row=row,
            column=0,
            sticky="w",
            padx=15,
            pady=7
        )

        entry = tk.Entry(
            form,
            width=30,
            font=("Arial", 11)
        )

        entry.insert(
            0,
            default
        )

        entry.grid(
            row=row,
            column=1,
            padx=15,
            pady=7
        )

        entries[label] = entry

    # Gender

    tk.Label(
        form,
        text="Gender",
        font=("Arial", 11, "bold"),
        bg="#dbeafe"
    ).grid(
        row=10,
        column=0,
        sticky="w",
        padx=15,
        pady=7
    )

    gender_box = ttk.Combobox(
        form,
        values=[
            "Male",
            "Female",
            "Other"
        ],
        state="readonly",
        width=28
    )

    gender_box.set("Male")

    gender_box.grid(
        row=10,
        column=1,
        padx=15,
        pady=7
    )

    def save_data():

        try:

            insert_record(

                entries["Student ID"].get(),

                entries["Student Name"].get(),

                gender_box.get(),

                entries["Department"].get(),

                entries["Semester"].get(),

                entries["Academic Year"].get(),

                entries["Study Hours / Day"].get(),

                entries["Attendance (%)"].get(),

                entries["Assignment Score"].get(),

                entries["Internal Marks"].get(),

                entries["Exam Score"].get()

            )

            update_dashboard()

            messagebox.showinfo(
                "Success",
                "Data successfully loaded into the Data Warehouse."
            )

            for entry in entries.values():

                entry.delete(
                    0,
                    "end"
                )

            entries["Academic Year"].insert(
                0,
                "2026-27"
            )

            gender_box.set("Male")

        except Exception as error:

            messagebox.showerror(
                "Invalid Data",
                str(error)
            )

    tk.Button(
        window,
        text="LOAD INTO DATA WAREHOUSE",
        command=save_data,
        font=("Arial", 13, "bold"),
        bg=GREEN,
        fg=WHITE,
        width=30,
        height=2,
        relief="flat"
    ).pack(
        pady=20
    )


# ================================================================
# CSV IMPORT / ETL
# ================================================================

def import_csv():

    file_path = filedialog.askopenfilename(

        title="Select Student CSV",

        filetypes=[
            ("CSV files", "*.csv"),
            ("All files", "*.*")
        ]
    )

    if not file_path:
        return

    try:

        # --------------------------------------------------------
        # EXTRACT
        # --------------------------------------------------------

        df = pd.read_csv(
            file_path
        )

        original_rows = len(df)

        # Normalize column names

        df.columns = [
            str(column)
            .strip()
            .lower()
            .replace(" ", "_")
            for column in df.columns
        ]

        # Common aliases

        aliases = {

            "id": "student_id",

            "student": "student_name",

            "name": "student_name",

            "dept": "department",

            "year": "academic_year",

            "study": "study_hours",

            "assignment": "assignment_score",

            "internal": "internal_marks",

            "exam": "exam_score"
        }

        df.rename(
            columns=aliases,
            inplace=True
        )

        required_columns = [

            "student_id",
            "student_name",
            "gender",
            "department",
            "semester",
            "academic_year",
            "study_hours",
            "attendance",
            "assignment_score",
            "internal_marks",
            "exam_score"
        ]

        missing_columns = [

            column
            for column in required_columns
            if column not in df.columns
        ]

        if missing_columns:

            raise ValueError(
                "Missing CSV columns:\n\n"
                + "\n".join(
                    missing_columns
                )
            )

        # --------------------------------------------------------
        # TRANSFORM
        # --------------------------------------------------------

        duplicate_count = int(
            df.duplicated().sum()
        )

        df = df.drop_duplicates()

        numeric_columns = [

            "semester",
            "study_hours",
            "attendance",
            "assignment_score",
            "internal_marks",
            "exam_score"
        ]

        for column in numeric_columns:

            df[column] = pd.to_numeric(
                df[column],
                errors="coerce"
            )

        missing_numeric = int(
            df[numeric_columns]
            .isna()
            .sum()
            .sum()
        )

        # Fill missing numeric values using median

        for column in numeric_columns:

            if df[column].isna().all():

                df[column] = 0

            else:

                df[column] = df[column].fillna(
                    df[column].median()
                )

        # Fill missing categorical values

        df["gender"] = df["gender"].fillna(
            "Other"
        )

        df["academic_year"] = df[
            "academic_year"
        ].fillna(
            "2026-27"
        )

        df["student_id"] = df[
            "student_id"
        ].astype(str)

        df["student_name"] = df[
            "student_name"
        ].fillna(
            "Unknown Student"
        )

        df["department"] = df[
            "department"
        ].fillna(
            "Unknown"
        )

        # Clip values to valid ranges

        df["semester"] = df[
            "semester"
        ].clip(1, 12)

        df["study_hours"] = df[
            "study_hours"
        ].clip(0, 24)

        df["attendance"] = df[
            "attendance"
        ].clip(0, 100)

        df["assignment_score"] = df[
            "assignment_score"
        ].clip(0, 100)

        df["internal_marks"] = df[
            "internal_marks"
        ].clip(0, 100)

        df["exam_score"] = df[
            "exam_score"
        ].clip(0, 100)

        removed_rows = (
            original_rows
            - len(df)
        )

        # --------------------------------------------------------
        # LOAD
        # --------------------------------------------------------

        loaded = 0

        for _, row in df.iterrows():

            try:

                insert_record(

                    row["student_id"],

                    row["student_name"],

                    row["gender"],

                    row["department"],

                    int(row["semester"]),

                    row["academic_year"],

                    row["study_hours"],

                    row["attendance"],

                    row["assignment_score"],

                    row["internal_marks"],

                    row["exam_score"]
                )

                loaded += 1

            except Exception:

                pass

        update_dashboard()

        messagebox.showinfo(

            "ETL Completed",

            f"""
EXTRACT
-------
Input Records: {original_rows}

TRANSFORM
---------
Duplicate Rows Removed: {duplicate_count}

Missing Numeric Values Processed:
{missing_numeric}

Rows Removed During Cleaning:
{removed_rows}

LOAD
----
Records Loaded:
{loaded}

Data Warehouse Updated Successfully.
"""
        )

    except Exception as error:

        messagebox.showerror(
            "CSV Import Error",
            str(error)
        )


# ================================================================
# DATA WAREHOUSE VIEWER
# ================================================================

def show_dataframe(
    title,
    dataframe
):

    window = tk.Toplevel(root)

    window.title(title)

    window.geometry(
        "1250x650"
    )

    tk.Label(
        window,
        text=title,
        font=("Arial", 20, "bold"),
        bg=NAVY,
        fg=WHITE,
        pady=12
    ).pack(fill="x")

    frame = tk.Frame(
        window
    )

    frame.pack(
        fill="both",
        expand=True,
        padx=10,
        pady=10
    )

    columns = list(
        dataframe.columns
    )

    tree = ttk.Treeview(
        frame,
        columns=columns,
        show="headings"
    )

    for column in columns:

        tree.heading(
            column,
            text=column
        )

        tree.column(
            column,
            width=130
        )

    for _, row in dataframe.iterrows():

        tree.insert(
            "",
            "end",
            values=list(row)
        )

    vertical = ttk.Scrollbar(
        frame,
        orient="vertical",
        command=tree.yview
    )

    horizontal = ttk.Scrollbar(
        frame,
        orient="horizontal",
        command=tree.xview
    )

    tree.configure(
        yscrollcommand=vertical.set,
        xscrollcommand=horizontal.set
    )

    tree.grid(
        row=0,
        column=0,
        sticky="nsew"
    )

    vertical.grid(
        row=0,
        column=1,
        sticky="ns"
    )

    horizontal.grid(
        row=1,
        column=0,
        sticky="ew"
    )

    frame.grid_rowconfigure(
        0,
        weight=1
    )

    frame.grid_columnconfigure(
        0,
        weight=1
    )


def warehouse_view():

    df = get_full_data()

    if df.empty:

        messagebox.showwarning(
            "No Data",
            "Add or import data first."
        )

        return

    show_dataframe(
        "INTEGRATED DATA WAREHOUSE",
        df
    )


# ================================================================
# INDIVIDUAL STAR SCHEMA TABLES
# ================================================================

def view_dimension_tables():

    tables = {

        "Student Dimension":
        "SELECT * FROM dim_student",

        "Department Dimension":
        "SELECT * FROM dim_department",

        "Semester Dimension":
        "SELECT * FROM dim_semester",

        "Time Dimension":
        "SELECT * FROM dim_time",

        "Fact Performance":
        "SELECT * FROM fact_performance"
    }

    window = tk.Toplevel(root)

    window.title(
        "Star Schema Tables"
    )

    window.geometry(
        "600x500"
    )

    window.configure(
        bg=WHITE
    )

    tk.Label(
        window,
        text="STAR SCHEMA TABLES",
        font=("Arial", 20, "bold"),
        bg=NAVY,
        fg=WHITE,
        pady=12
    ).pack(fill="x")

    for title, query in tables.items():

        def open_table(
            q=query,
            t=title
        ):

            df = pd.read_sql_query(
                q,
                conn
            )

            show_dataframe(
                t,
                df
            )

        tk.Button(
            window,
            text=title,
            command=open_table,
            font=("Arial", 11, "bold"),
            bg=TEAL,
            fg=WHITE,
            width=30,
            height=2,
            relief="flat"
        ).pack(
            pady=8
        )


# ================================================================
# STAR SCHEMA ARCHITECTURE
# ================================================================

def star_schema():

    architecture = """

                    STAR SCHEMA
                    ============


                      DIM_STUDENT
                           |
                           |
                           |
DIM_DEPARTMENT ---- FACT_PERFORMANCE ---- DIM_TIME
                           |
                           |
                           |
                     DIM_SEMESTER



FACT TABLE
==========

FACT_PERFORMANCE

Measures:

• Study Hours
• Attendance
• Assignment Score
• Internal Marks
• Exam Score
• Performance Category



DIMENSION TABLES
================

1. DIM_STUDENT

   • Student Key
   • Student ID
   • Student Name
   • Gender


2. DIM_DEPARTMENT

   • Department Key
   • Department Name


3. DIM_SEMESTER

   • Semester Key
   • Semester Number


4. DIM_TIME

   • Time Key
   • Academic Year



DATA WAREHOUSE FLOW
===================

Source Data
     ↓
Extract
     ↓
Transform
     ↓
Clean
     ↓
Load
     ↓
Star Schema
     ↓
OLAP
     ↓
Data Mining
     ↓
Prediction
     ↓
Visualization
"""

    create_text_window(
        "Star Schema Architecture",
        architecture,
        850,
        650
    )


# ================================================================
# ETL REPORT
# ================================================================

def etl_report():

    df = get_full_data()

    if df.empty:

        messagebox.showwarning(
            "No Data",
            "No warehouse data available."
        )

        return

    missing = int(
        df.isna().sum().sum()
    )

    duplicate = int(
        df.duplicated().sum()
    )

    report = f"""

ETL PROCESSING REPORT
=====================


1. EXTRACT
----------

Data Source:
CSV / User Input

Warehouse Records:
{len(df)}


2. TRANSFORM
------------

Data Cleaning:

✓ Duplicate detection
✓ Missing value handling
✓ Numeric conversion
✓ Range validation
✓ Categorical value handling
✓ Performance categorization


Missing Cells:
{missing}

Duplicate Integrated Rows:
{duplicate}


3. LOAD
-------

Data is loaded into:

• dim_student
• dim_department
• dim_semester
• dim_time
• fact_performance


4. PERFORMANCE TRANSFORMATION
-----------------------------

Exam Score >= 75
        ↓
      GOOD

Exam Score 50 - 74
        ↓
     AVERAGE

Exam Score < 50
        ↓
      POOR


ETL STATUS
==========

DATA READY FOR OLAP AND DATA MINING
"""

    create_text_window(
        "ETL Report",
        report
    )


# ================================================================
# OLAP WINDOW
# ================================================================

def olap_analysis():

    df = get_full_data()

    if df.empty:

        messagebox.showwarning(
            "No Data",
            "Add data first."
        )

        return

    window = tk.Toplevel(root)

    window.title(
        "OLAP Analysis"
    )

    window.geometry(
        "1050x700"
    )

    window.configure(
        bg=WHITE
    )

    tk.Label(
        window,
        text="OLAP ANALYSIS",
        font=("Arial", 21, "bold"),
        bg=PURPLE,
        fg=WHITE,
        pady=12
    ).pack(fill="x")

    controls = tk.Frame(
        window,
        bg=WHITE
    )

    controls.pack(
        pady=15
    )

    tk.Label(
        controls,
        text="Operation:",
        font=("Arial", 11, "bold"),
        bg=WHITE
    ).grid(
        row=0,
        column=0,
        padx=8
    )

    operations = [

        "Roll-up by Department",

        "Drill-down by Semester",

        "Slice by Department",

        "Slice by Semester",

        "Dice: Good Students",

        "Dice: High Attendance"
    ]

    operation_box = ttk.Combobox(
        controls,
        values=operations,
        state="readonly",
        width=28
    )

    operation_box.set(
        operations[0]
    )

    operation_box.grid(
        row=0,
        column=1,
        padx=8
    )

    # Department

    departments = sorted(
        df["department_name"]
        .unique()
        .tolist()
    )

    tk.Label(
        controls,
        text="Department:",
        font=("Arial", 11, "bold"),
        bg=WHITE
    ).grid(
        row=0,
        column=2,
        padx=8
    )

    department_box = ttk.Combobox(
        controls,
        values=departments,
        state="readonly",
        width=20
    )

    if departments:
        department_box.set(
            departments[0]
        )

    department_box.grid(
        row=0,
        column=3,
        padx=8
    )

    # Semester

    semesters = sorted(
        df["semester_number"]
        .unique()
        .tolist()
    )

    tk.Label(
        controls,
        text="Semester:",
        font=("Arial", 11, "bold"),
        bg=WHITE
    ).grid(
        row=1,
        column=0,
        padx=8,
        pady=10
    )

    semester_box = ttk.Combobox(
        controls,
        values=semesters,
        state="readonly",
        width=28
    )

    if semesters:
        semester_box.set(
            semesters[0]
        )

    semester_box.grid(
        row=1,
        column=1,
        padx=8
    )

    result = tk.Text(
        window,
        font=("Consolas", 11)
    )

    result.pack(
        fill="both",
        expand=True,
        padx=20,
        pady=10
    )

    def run_olap():

        operation = operation_box.get()

        try:

            # ----------------------------------------------------
            # ROLL-UP
            # ----------------------------------------------------

            if operation == "Roll-up by Department":

                output = df.groupby(
                    "department_name"
                ).agg(

                    Students=(
                        "student_name",
                        "count"
                    ),

                    Average_Exam=(
                        "exam_score",
                        "mean"
                    ),

                    Average_Attendance=(
                        "attendance",
                        "mean"
                    )
                ).round(2)

            # ----------------------------------------------------
            # DRILL-DOWN
            # ----------------------------------------------------

            elif operation == "Drill-down by Semester":

                output = df.groupby(
                    [
                        "department_name",
                        "semester_number"
                    ]
                ).agg(

                    Students=(
                        "student_name",
                        "count"
                    ),

                    Average_Exam=(
                        "exam_score",
                        "mean"
                    ),

                    Average_Attendance=(
                        "attendance",
                        "mean"
                    )
                ).round(2)

            # ----------------------------------------------------
            # SLICE DEPARTMENT
            # ----------------------------------------------------

            elif operation == "Slice by Department":

                output = df[
                    df["department_name"]
                    == department_box.get()
                ][
                    [
                        "student_id",
                        "student_name",
                        "semester_number",
                        "exam_score",
                        "attendance",
                        "performance"
                    ]
                ]

            # ----------------------------------------------------
            # SLICE SEMESTER
            # ----------------------------------------------------

            elif operation == "Slice by Semester":

                selected_semester = int(
                    semester_box.get()
                )

                output = df[
                    df["semester_number"]
                    == selected_semester
                ][
                    [
                        "student_id",
                        "student_name",
                        "department_name",
                        "exam_score",
                        "attendance",
                        "performance"
                    ]
                ]

            # ----------------------------------------------------
            # DICE
            # ----------------------------------------------------

            elif operation == "Dice: Good Students":

                output = df[
                    (
                        df["performance"]
                        == "Good"
                    )
                    &
                    (
                        df["attendance"]
                        >= 75
                    )
                ][
                    [
                        "student_id",
                        "student_name",
                        "department_name",
                        "semester_number",
                        "attendance",
                        "exam_score"
                    ]
                ]

            # ----------------------------------------------------
            # DICE HIGH ATTENDANCE
            # ----------------------------------------------------

            else:

                output = df[
                    df["attendance"]
                    >= 85
                ][
                    [
                        "student_id",
                        "student_name",
                        "department_name",
                        "semester_number",
                        "attendance",
                        "exam_score",
                        "performance"
                    ]
                ]

            result.delete(
                "1.0",
                "end"
            )

            result.insert(
                "1.0",
                output.to_string(
                    index=False
                )
            )

        except Exception as error:

            messagebox.showerror(
                "OLAP Error",
                str(error)
            )

    tk.Button(
        controls,
        text="RUN OLAP",
        command=run_olap,
        bg=PURPLE,
        fg=WHITE,
        font=("Arial", 11, "bold"),
        width=15
    ).grid(
        row=1,
        column=3,
        padx=10
    )


# ================================================================
# CLASSIFICATION
# ================================================================

def classification():

    df = get_full_data()

    if len(df) < 12:

        messagebox.showwarning(
            "Insufficient Data",
            "Add at least 12 records for classification."
        )

        return

    features = [

        "study_hours",

        "attendance",

        "assignment_score",

        "internal_marks"
    ]

    X = df[features]

    y = df["performance"]

    if y.nunique() < 2:

        messagebox.showwarning(
            "Insufficient Classes",
            "Dataset must contain at least two performance classes."
        )

        return

    # Check minimum samples

    if y.value_counts().min() < 2:

        messagebox.showwarning(
            "Insufficient Class Samples",
            "Each performance class should have at least 2 records."
        )

        return

    X_train, X_test, y_train, y_test = train_test_split(

        X,
        y,

        test_size=0.25,

        random_state=42,

        stratify=y
    )

    # Decision Tree

    decision_tree = DecisionTreeClassifier(

        max_depth=5,

        random_state=42
    )

    decision_tree.fit(
        X_train,
        y_train
    )

    dt_prediction = decision_tree.predict(
        X_test
    )

    dt_accuracy = accuracy_score(
        y_test,
        dt_prediction
    )

    # Random Forest

    random_forest = RandomForestClassifier(

        n_estimators=150,

        random_state=42
    )

    random_forest.fit(
        X_train,
        y_train
    )

    rf_prediction = random_forest.predict(
        X_test
    )

    rf_accuracy = accuracy_score(
        y_test,
        rf_prediction
    )

    report = f"""

DATA MINING - CLASSIFICATION
============================


DATASET
=======

Total Records:
{len(df)}

Training Records:
{len(X_train)}

Testing Records:
{len(X_test)}


INPUT FEATURES
==============

1. Study Hours
2. Attendance
3. Assignment Score
4. Internal Marks


TARGET VARIABLE
===============

Performance

• Good
• Average
• Poor


DECISION TREE
=============

Accuracy:
{dt_accuracy * 100:.2f}%


RANDOM FOREST
=============

Accuracy:
{rf_accuracy * 100:.2f}%


RANDOM FOREST CLASSIFICATION REPORT
===================================

{classification_report(
    y_test,
    rf_prediction,
    zero_division=0
)}
"""

    window = create_text_window(
        "Classification Results",
        report,
        950,
        700
    )

    tk.Button(
        window,
        text="SHOW DECISION TREE",
        command=lambda:
            show_decision_tree(
                decision_tree,
                features
            ),
        bg=BLUE,
        fg=WHITE,
        font=("Arial", 11, "bold")
    ).pack(
        pady=10
    )


# ================================================================
# DECISION TREE VISUALIZATION
# ================================================================

def show_decision_tree(
    model,
    features
):

    plt.figure(
        figsize=(17, 10)
    )

    plot_tree(

        model,

        feature_names=features,

        class_names=list(
            model.classes_
        ),

        filled=True,

        rounded=True
    )

    plt.title(
        "Decision Tree - Student Performance Classification"
    )

    plt.tight_layout()

    plt.show()


# ================================================================
# RANDOM FOREST FEATURE IMPORTANCE
# ================================================================

def feature_importance():

    df = get_full_data()

    if len(df) < 10:

        messagebox.showwarning(
            "Insufficient Data",
            "Add at least 10 records."
        )

        return

    if df["performance"].nunique() < 2:

        messagebox.showwarning(
            "Insufficient Classes",
            "At least two performance classes are required."
        )

        return

    features = [

        "study_hours",

        "attendance",

        "assignment_score",

        "internal_marks"
    ]

    model = RandomForestClassifier(

        n_estimators=150,

        random_state=42
    )

    model.fit(
        df[features],
        df["performance"]
    )

    importance = pd.Series(

        model.feature_importances_,

        index=features
    ).sort_values()

    plt.figure(
        figsize=(9, 5)
    )

    importance.plot(
        kind="barh"
    )

    plt.title(
        "Random Forest Feature Importance"
    )

    plt.xlabel(
        "Importance"
    )

    plt.tight_layout()

    plt.show()


# ================================================================
# K-MEANS CLUSTERING
# ================================================================

def clustering():

    df = get_full_data()

    if len(df) < 6:

        messagebox.showwarning(
            "Insufficient Data",
            "Add at least 6 records for clustering."
        )

        return

    features = [

        "study_hours",

        "attendance",

        "assignment_score",

        "exam_score"
    ]

    scaler = StandardScaler()

    X = scaler.fit_transform(
        df[features]
    )

    kmeans = KMeans(

        n_clusters=3,

        n_init=10,

        random_state=42
    )

    clusters = kmeans.fit_predict(
        X
    )

    result = df.copy()

    result["cluster"] = clusters

    centers = scaler.inverse_transform(
        kmeans.cluster_centers_
    )

    centers_df = pd.DataFrame(
        centers,
        columns=features
    )

    report = """

K-MEANS CLUSTERING
==================


FEATURES
--------

Study Hours
Attendance
Assignment Score
Exam Score


STUDENT CLUSTERS
================

"""

    report += result[
        [
            "student_id",
            "student_name",
            "department_name",
            "exam_score",
            "cluster"
        ]
    ].to_string(
        index=False
    )

    report += """



CLUSTER CENTERS
===============
"""

    report += centers_df.round(
        2
    ).to_string(
        index=False
    )

    create_text_window(
        "K-Means Clustering",
        report,
        1000,
        700
    )

    # Visualization

    plt.figure(
        figsize=(9, 6)
    )

    plt.scatter(

        result["study_hours"],

        result["exam_score"],

        c=result["cluster"],

        s=80
    )

    plt.xlabel(
        "Study Hours"
    )

    plt.ylabel(
        "Exam Score"
    )

    plt.title(
        "K-Means Student Clustering"
    )

    plt.grid(True)

    plt.tight_layout()

    plt.show()


# ================================================================
# PERFORMANCE PREDICTION
# ================================================================

def prediction():

    df = get_full_data()

    if len(df) < 10:

        messagebox.showwarning(
            "Insufficient Data",
            "Add at least 10 records before prediction."
        )

        return

    if df["performance"].nunique() < 2:

        messagebox.showwarning(
            "Insufficient Classes",
            "Dataset needs at least two performance classes."
        )

        return

    features = [

        "study_hours",

        "attendance",

        "assignment_score",

        "internal_marks"
    ]

    model = RandomForestClassifier(

        n_estimators=150,

        random_state=42
    )

    model.fit(
        df[features],
        df["performance"]
    )

    window = tk.Toplevel(root)

    window.title(
        "Student Performance Prediction"
    )

    window.geometry(
        "600x650"
    )

    window.configure(
        bg="#e0f2fe"
    )

    tk.Label(
        window,
        text="PREDICT STUDENT PERFORMANCE",
        font=("Arial", 19, "bold"),
        bg=CYAN,
        fg=WHITE,
        pady=14
    ).pack(
        fill="x"
    )

    form = tk.Frame(
        window,
        bg="#e0f2fe"
    )

    form.pack(
        pady=30
    )

    fields = [

        ("Study Hours", "study"),

        ("Attendance (%)", "attendance"),

        ("Assignment Score", "assignment"),

        ("Internal Marks", "internal")
    ]

    entries = {}

    for row, (label, key) in enumerate(fields):

        tk.Label(
            form,
            text=label,
            font=("Arial", 12, "bold"),
            bg="#e0f2fe"
        ).grid(
            row=row,
            column=0,
            padx=15,
            pady=12,
            sticky="w"
        )

        entry = tk.Entry(
            form,
            width=25,
            font=("Arial", 12)
        )

        entry.grid(
            row=row,
            column=1,
            padx=15,
            pady=12
        )

        entries[key] = entry

    result_label = tk.Label(

        window,

        text="Prediction will appear here",

        font=("Arial", 17, "bold"),

        bg="#e0f2fe",

        fg=DARK
    )

    result_label.pack(
        pady=25
    )

    confidence_label = tk.Label(

        window,

        text="",

        font=("Arial", 12),

        bg="#e0f2fe",

        fg=GRAY
    )

    confidence_label.pack()

    def predict_result():

        try:

            values = [

                safe_float(
                    entries["study"].get(),
                    0,
                    24,
                    "Study Hours"
                ),

                safe_float(
                    entries["attendance"].get(),
                    0,
                    100,
                    "Attendance"
                ),

                safe_float(
                    entries["assignment"].get(),
                    0,
                    100,
                    "Assignment Score"
                ),

                safe_float(
                    entries["internal"].get(),
                    0,
                    100,
                    "Internal Marks"
                )
            ]

            sample = pd.DataFrame(
                [values],
                columns=features
            )

            prediction_value = model.predict(
                sample
            )[0]

            probabilities = model.predict_proba(
                sample
            )[0]

            confidence = (
                np.max(probabilities)
                * 100
            )

            result_label.config(

                text=
                f"Predicted Performance: "
                f"{prediction_value}"
            )

            confidence_label.config(

                text=
                f"Model confidence: "
                f"{confidence:.2f}%"
            )

        except Exception as error:

            messagebox.showerror(
                "Prediction Error",
                str(error)
            )

    tk.Button(

        window,

        text="PREDICT",

        command=predict_result,

        bg=GREEN,

        fg=WHITE,

        font=("Arial", 13, "bold"),

        width=20,

        height=2
    ).pack(
        pady=15
    )


# ================================================================
# CHARTS
# ================================================================

def performance_chart():

    df = get_full_data()

    if df.empty:

        messagebox.showwarning(
            "No Data",
            "Add data first."
        )

        return

    df["performance"].value_counts().plot(
        kind="bar",
        figsize=(8, 5)
    )

    plt.title(
        "Student Performance Distribution"
    )

    plt.xlabel(
        "Performance"
    )

    plt.ylabel(
        "Number of Students"
    )

    plt.tight_layout()

    plt.show()


def department_chart():

    df = get_full_data()

    if df.empty:
        return

    average = df.groupby(
        "department_name"
    )["exam_score"].mean()

    average.plot(
        kind="bar",
        figsize=(9, 5)
    )

    plt.title(
        "Average Exam Score by Department"
    )

    plt.xlabel(
        "Department"
    )

    plt.ylabel(
        "Average Exam Score"
    )

    plt.tight_layout()

    plt.show()


def semester_chart():

    df = get_full_data()

    if df.empty:
        return

    average = df.groupby(
        "semester_number"
    )["exam_score"].mean()

    average.plot(
        kind="line",
        marker="o",
        figsize=(9, 5)
    )

    plt.title(
        "Average Exam Score by Semester"
    )

    plt.xlabel(
        "Semester"
    )

    plt.ylabel(
        "Average Exam Score"
    )

    plt.grid(True)

    plt.tight_layout()

    plt.show()


def attendance_chart():

    df = get_full_data()

    if df.empty:
        return

    plt.figure(
        figsize=(9, 5)
    )

    plt.scatter(

        df["attendance"],

        df["exam_score"],

        s=80
    )

    plt.title(
        "Attendance vs Exam Score"
    )

    plt.xlabel(
        "Attendance (%)"
    )

    plt.ylabel(
        "Exam Score"
    )

    plt.grid(True)

    plt.tight_layout()

    plt.show()


def study_chart():

    df = get_full_data()

    if df.empty:
        return

    plt.figure(
        figsize=(9, 5)
    )

    plt.scatter(

        df["study_hours"],

        df["exam_score"],

        s=80
    )

    plt.title(
        "Study Hours vs Exam Score"
    )

    plt.xlabel(
        "Study Hours"
    )

    plt.ylabel(
        "Exam Score"
    )

    plt.grid(True)

    plt.tight_layout()

    plt.show()


def assignment_chart():

    df = get_full_data()

    if df.empty:
        return

    plt.figure(
        figsize=(9, 5)
    )

    plt.scatter(

        df["assignment_score"],

        df["exam_score"],

        s=80
    )

    plt.title(
        "Assignment Score vs Exam Score"
    )

    plt.xlabel(
        "Assignment Score"
    )

    plt.ylabel(
        "Exam Score"
    )

    plt.grid(True)

    plt.tight_layout()

    plt.show()


# ================================================================
# EXPORT
# ================================================================

def export_csv():

    df = get_full_data()

    if df.empty:

        messagebox.showwarning(
            "No Data",
            "There is no data to export."
        )

        return

    path = filedialog.asksaveasfilename(

        title="Export Warehouse Data",

        defaultextension=".csv",

        filetypes=[
            ("CSV files", "*.csv")
        ]
    )

    if not path:
        return

    try:

        df.to_csv(
            path,
            index=False
        )

        messagebox.showinfo(
            "Export Complete",
            "Warehouse data exported successfully."
        )

    except Exception as error:

        messagebox.showerror(
            "Export Error",
            str(error)
        )


# ================================================================
# DATABASE STATUS
# ================================================================

def database_status():

    tables = [

        "dim_student",

        "dim_department",

        "dim_semester",

        "dim_time",

        "fact_performance"
    ]

    text = """

DATA WAREHOUSE DATABASE STATUS
==============================


DATABASE FILE
-------------

"""

    text += DB_NAME

    text += "\n\nTABLE RECORD COUNTS\n"
    text += "===================\n\n"

    for table in tables:

        cursor.execute(
            f"SELECT COUNT(*) FROM {table}"
        )

        count = cursor.fetchone()[0]

        text += (
            f"{table:<25}"
            f"{count:>8} records\n"
        )

    text += """



DATABASE TYPE
-------------

SQLite


SCHEMA
------

Star Schema


STATUS
------

READY
"""

    create_text_window(
        "Database Status",
        text,
        700,
        500
    )


# ================================================================
# CLEAR DATABASE
# ================================================================

def clear_database():

    answer = messagebox.askyesno(

        "Clear Warehouse",

        "Are you sure you want to delete ALL warehouse data?"
    )

    if not answer:
        return

    cursor.execute(
        "DELETE FROM fact_performance"
    )

    cursor.execute(
        "DELETE FROM dim_student"
    )

    cursor.execute(
        "DELETE FROM dim_department"
    )

    cursor.execute(
        "DELETE FROM dim_semester"
    )

    cursor.execute(
        "DELETE FROM dim_time"
    )

    conn.commit()

    update_dashboard()

    messagebox.showinfo(
        "Warehouse Cleared",
        "All warehouse records have been deleted."
    )


# ================================================================
# BUTTON CREATOR
# ================================================================

def create_menu_button(
    parent,
    text,
    command,
    color
):

    return tk.Button(

        parent,

        text=text,

        command=command,

        font=("Arial", 11, "bold"),

        bg=color,

        fg=WHITE,

        relief="flat",

        width=31,

        height=2,

        cursor="hand2"
    )


# ================================================================
# HEADER
# ================================================================

header = tk.Frame(
    root,
    bg=NAVY,
    height=85
)

header.pack(
    fill="x"
)

tk.Label(

    header,

    text="DWDM",

    font=("Arial", 30, "bold"),

    bg=NAVY,

    fg=WHITE
).pack(

    side="left",

    padx=30,

    pady=18
)

tk.Label(

    header,

    text=
    "Smart Student Performance "
    "Data Warehouse & Data Mining System",

    font=("Arial", 16),

    bg=NAVY,

    fg="#bfdbfe"
).pack(

    side="left"
)


# ================================================================
# DASHBOARD CARDS
# ================================================================

cards = tk.Frame(
    root,
    bg=LIGHT
)

cards.pack(
    fill="x",
    padx=25,
    pady=18
)


def dashboard_card(
    title,
    variable,
    color
):

    frame = tk.Frame(

        cards,

        bg=color,

        height=105
    )

    frame.pack(

        side="left",

        fill="both",

        expand=True,

        padx=7
    )

    frame.pack_propagate(
        False
    )

    tk.Label(

        frame,

        text=title,

        font=("Arial", 11, "bold"),

        bg=color,

        fg=WHITE
    ).pack(
        pady=(13, 3)
    )

    tk.Label(

        frame,

        textvariable=variable,

        font=("Arial", 24, "bold"),

        bg=color,

        fg=WHITE
    ).pack()


dashboard_card(
    "TOTAL RECORDS",
    total_records,
    BLUE
)

dashboard_card(
    "AVERAGE EXAM",
    average_exam,
    GREEN
)

dashboard_card(
    "AVERAGE ATTENDANCE",
    average_attendance,
    PURPLE
)

dashboard_card(
    "GOOD PERFORMERS",
    good_students,
    ORANGE
)

dashboard_card(
    "DEPARTMENTS",
    departments_count,
    TEAL
)


# ================================================================
# MAIN CONTENT
# ================================================================

main = tk.Frame(
    root,
    bg=LIGHT
)

main.pack(
    fill="both",
    expand=True,
    padx=25,
    pady=5
)


# ================================================================
# LEFT SIDEBAR
# ================================================================

left = tk.Frame(

    main,

    bg=WHITE,

    width=365
)

left.pack(

    side="left",

    fill="y",

    padx=(0, 15)
)

left.pack_propagate(
    False
)

tk.Label(

    left,

    text="PROJECT MODULES",

    font=("Arial", 17, "bold"),

    bg=WHITE,

    fg=DARK
).pack(
    pady=15
)


create_menu_button(
    left,
    "Add Student Data",
    add_data_window,
    BLUE
).pack(pady=3)

create_menu_button(
    left,
    "Import CSV / Run ETL",
    import_csv,
    ORANGE
).pack(pady=3)

create_menu_button(
    left,
    "View Integrated Warehouse",
    warehouse_view,
    PURPLE
).pack(pady=3)

create_menu_button(
    left,
    "View Star Schema",
    star_schema,
    TEAL
).pack(pady=3)

create_menu_button(
    left,
    "View Dimension / Fact Tables",
    view_dimension_tables,
    CYAN
).pack(pady=3)

create_menu_button(
    left,
    "ETL Report",
    etl_report,
    GREEN
).pack(pady=3)

create_menu_button(
    left,
    "OLAP Analysis",
    olap_analysis,
    PURPLE
).pack(pady=3)

create_menu_button(
    left,
    "Decision Tree + Random Forest",
    classification,
    BLUE
).pack(pady=3)

create_menu_button(
    left,
    "Feature Importance",
    feature_importance,
    TEAL
).pack(pady=3)

create_menu_button(
    left,
    "K-Means Clustering",
    clustering,
    ORANGE
).pack(pady=3)

create_menu_button(
    left,
    "Predict New Student",
    prediction,
    GREEN
).pack(pady=3)

create_menu_button(
    left,
    "Export Warehouse CSV",
    export_csv,
    BLUE
).pack(pady=3)

create_menu_button(
    left,
    "Database Status",
    database_status,
    RED
).pack(pady=3)

create_menu_button(
    left,
    "Clear Warehouse",
    clear_database,
    RED
).pack(pady=3)


# ================================================================
# RIGHT ANALYTICS PANEL
# ================================================================

right = tk.Frame(
    main,
    bg=WHITE
)

right.pack(
    side="right",
    fill="both",
    expand=True
)


tk.Label(

    right,

    text="ANALYTICS & VISUALIZATION",

    font=("Arial", 21, "bold"),

    bg=WHITE,

    fg=NAVY
).pack(
    pady=18
)


chart_frame = tk.Frame(
    right,
    bg=WHITE
)

chart_frame.pack(
    pady=5
)


chart_buttons = [

    (
        "Performance Distribution",
        performance_chart,
        BLUE
    ),

    (
        "Department Analysis",
        department_chart,
        PURPLE
    ),

    (
        "Semester Trend",
        semester_chart,
        GREEN
    ),

    (
        "Attendance vs Exam",
        attendance_chart,
        ORANGE
    ),

    (
        "Study Hours vs Exam",
        study_chart,
        TEAL
    ),

    (
        "Assignment vs Exam",
        assignment_chart,
        CYAN
    )
]


for index, (
    title,
    command,
    color
) in enumerate(chart_buttons):

    create_menu_button(

        chart_frame,

        "📊 " + title,

        command,

        color

    ).grid(

        row=index,

        column=0,

        padx=10,

        pady=4
    )


# ================================================================
# WORKFLOW DISPLAY
# ================================================================

workflow = """

DWDM PROJECT WORKFLOW

DATA SOURCE
     ↓
EXTRACT
     ↓
TRANSFORM
     ↓
DATA CLEANING
     ↓
LOAD
     ↓
STAR SCHEMA DATA WAREHOUSE
     ↓
OLAP ANALYSIS
     ↓
DATA MINING
     ↓
DECISION TREE + RANDOM FOREST
     ↓
K-MEANS CLUSTERING
     ↓
PERFORMANCE PREDICTION
     ↓
VISUALIZATION & REPORTING
"""


tk.Label(

    right,

    text=workflow,

    font=("Arial", 12, "bold"),

    bg=WHITE,

    fg=DARK,

    justify="center"
).pack(
    pady=10
)


tk.Label(

    right,

    text=
    "Python • Tkinter • SQLite • Pandas • NumPy • "
    "Scikit-learn • Matplotlib",

    font=("Arial", 10),

    bg=WHITE,

    fg=GRAY
).pack(
    pady=5
)


# ================================================================
# CLOSE APPLICATION
# ================================================================

def close_application():

    conn.close()

    root.destroy()


root.protocol(
    "WM_DELETE_WINDOW",
    close_application
)


# ================================================================
# START
# ================================================================

update_dashboard()

root.mainloop()