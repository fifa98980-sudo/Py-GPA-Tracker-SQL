import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import os


class AcademicManager:
    def __init__(self, db_name="student_data.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self._init_db()

    def _init_db(self):
        # Create table with an auto-incrementing ID
        self.cursor.execute('''
                            CREATE TABLE IF NOT EXISTS courses
                            (
                                id
                                INTEGER
                                PRIMARY
                                KEY
                                AUTOINCREMENT,
                                name
                                TEXT,
                                credits
                                INTEGER,
                                grade
                                REAL
                            )
                            ''')
        self.conn.commit()

    def add_course(self, name, credits, grade):
        self.cursor.execute('INSERT INTO courses (name, credits, grade) VALUES (?, ?, ?)',
                            (name, credits, grade))
        self.conn.commit()
        print(">> Course added successfully.")

    def delete_course(self, course_id):
        # SQL command to delete a specific row by ID
        self.cursor.execute("DELETE FROM courses WHERE id=?", (course_id,))
        self.conn.commit()

        # Check if anything was actually deleted
        if self.cursor.rowcount > 0:
            print(f">> Course ID {course_id} deleted successfully.")
        else:
            print(">> Error: ID not found.")

    def get_data(self):
        return pd.read_sql_query("SELECT * FROM courses", self.conn)

    def get_gpa(self):
        df = self.get_data()
        if df.empty:
            return 0.0

        total_pts = sum(df['grade'] * df['credits'])
        total_credits = df['credits'].sum()
        return round(total_pts / total_credits, 2)

    def show_stats(self):
        df = self.get_data()
        if df.empty:
            print("No data available.")
            return

        print("\n--- 📊 Quick Statistics ---")
        print(f"Total Courses: {len(df)}")
        print(f"Current GPA:   {self.get_gpa()}%")
        print(f"Highest Grade: {df['grade'].max()}%")
        print("---------------------------")

    def show_graph(self):
        df = self.get_data()
        if df.empty:
            print("No data to plot.")
            return

        plt.figure(figsize=(10, 6))
        colors = ['#4CAF50' if x >= 90 else '#FFC107' if x >= 80 else '#F44336' for x in df['grade']]

        plt.bar(df['name'], df['grade'], color=colors)
        gpa = self.get_gpa()
        plt.axhline(y=gpa, color='blue', linestyle='--', label=f'GPA: {gpa}')

        plt.ylabel("Grade (%)")
        plt.title("ScholarMetrics Analysis")
        plt.ylim(0, 105)
        plt.legend()
        plt.show()

    def close(self):
        self.conn.close()


# --- Main Interface ---
if __name__ == "__main__":
    app = AcademicManager()

    while True:
        print("\n=== 🎓 ScholarMetrics: GPA Manager ===")
        print("1. Add New Course")
        print("2. Show Statistics")
        print("3. Visualize Data (Graph)")
        print("4. Delete Course (New)")  # <--- الخيار الجديد
        print("5. Exit")

        choice = input("Select option (1-5): ").strip()

        if choice == '1':
            name = input("Course Name: ")
            try:
                cr = int(input("Credits: "))
                gr = float(input("Grade: "))
                if 0 <= gr <= 100:
                    app.add_course(name, cr, gr)
                else:
                    print("Error: Grade must be 0-100")
            except ValueError:
                print("Error: Invalid input.")

        elif choice == '2':
            app.show_stats()

        elif choice == '3':
            print(">> Generating Graph...")
            app.show_graph()

        elif choice == '4':
            # 1. Show existing data first so user knows the ID
            df = app.get_data()
            if df.empty:
                print("No courses to delete.")
            else:
                print("\n--- 🗑️ Delete Course ---")
                print(df.to_string(index=False))  # Show table nicely
                print("------------------------")
                try:
                    target_id = int(input("Enter the ID of the course to delete: "))
                    app.delete_course(target_id)
                except ValueError:
                    print("Error: Please enter a valid ID number.")

        elif choice == '5':
            print("Exiting...")
            app.close()
            break

        else:
            print("Invalid option.")