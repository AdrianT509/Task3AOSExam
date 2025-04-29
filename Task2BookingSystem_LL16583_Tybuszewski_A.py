import sqlite3
from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
from sqlite3 import Error

app = Flask(__name__)

# The SQLite3 database connection
def DB_connection():
    conn = sqlite3.connect('Booking_System Database.db')
    conn.row_factory = sqlite3.Row
    return conn

# Creates the Bookings Table
def BookingTable():
    conn = DB_connection()
    cursor = conn.cursor()
    cursor.execute(""" 
        CREATE TABLE IF NOT EXISTS Bookings (
            BookingID INTEGER PRIMARY KEY AUTOINCREMENT,
            BookingType TEXT NOT NULL,
            ServiceType TEXT NOT NULL,
            Date TEXT NOT NULL
        )
    """)
    cursor.execute("SELECT * FROM Bookings;")
    conn.commit()
    conn.close()

# Creates the Form Table with a foreign key referencing BookingID
def BookingForm():
    conn = DB_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Form (
            BookingID INTEGER PRIMARY KEY,
            FirstName TEXT NOT NULL,
            LastName TEXT NOT NULL,
            Email TEXT NOT NULL,
            Phone TEXT NOT NULL,
            Address TEXT NOT NULL,
            Time TEXT NOT NULL,
            FOREIGN KEY(BookingID) REFERENCES Bookings(BookingID)
        )
    """)
    conn.commit()
    conn.close()

# Route for booking creation
@app.route('/book', methods=['GET', 'POST'])
def book():
    if request.method == 'POST':
        booking_type = request.form['booking_type']
        service_type = request.form['service_type']
        selected_date = request.form['selected_date']  # Get the selected date

        print(f"Selected Date: {selected_date}")  # Debugging line

        try:
            # Try parsing the date in the 'DD-Mon-YYYY' format (e.g., 08-Jan-2025)
            parsed_date = datetime.strptime(selected_date, '%d-%b-%Y')

            # Convert the date to 'YYYY-MM-DD' format
            formatted_date = parsed_date.strftime('%Y-%m-%d')

            print(f"Formatted Date: {formatted_date}")  # Debugging line

            # Use `with` to automatically handle the connection and cursor
            with DB_connection() as conn:
                cursor = conn.cursor()

                # Insert the booking into the database
                cursor.execute("INSERT INTO Bookings (BookingType, ServiceType, Date) VALUES (?, ?, ?)", 
                               (booking_type, service_type, formatted_date))
                conn.commit()

                # Get the BookingID of the last inserted booking
                booking_id = cursor.lastrowid
                print(f"Generated BookingID: {booking_id}")  # Debugging line

                # Redirect to the next page for form submission and pass the BookingID
                return redirect(url_for('submit_booking', booking_id=booking_id))

        except Error as e:
            return f"An error occurred while inserting the booking: {e}"

        except ValueError:
            return "Invalid Date format. Please Choose a Valid Date."

    return render_template('Booking Page 1.html')  # Render booking form for GET request


# Route to handle the booking form submission
@app.route('/submit', methods=['GET', 'POST'])
def submit_booking():
    booking_id = request.args.get('booking_id')  # Get the BookingID from URL
    print(f"BookingID from URL: {booking_id}")  # Debugging line

    if request.method == 'POST':
        first_name = request.form['fname']
        last_name = request.form['lname']
        email = request.form['email']
        phone = request.form['phone']
        address = request.form['address']
        time = request.form['time']

        # Debugging: print the form data
        print(f"Form Data: {first_name}, {last_name}, {email}, {phone}, {address}, {time}")

        try:
            with DB_connection() as conn:
                cursor = conn.cursor()

                cursor.execute("""
                    INSERT INTO Form (BookingID, FirstName, LastName, Email, Phone, Address, Time)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (booking_id, first_name, last_name, email, phone, address, time))
                conn.commit()

                print(f"Form data for BookingID {booking_id} inserted successfully.")  # Debugging line

            return redirect(url_for('Success'))
        
        except sqlite3.Error as e:
            print(f"Error while submitting form data: {e}")
            return f"An error occurred while submitting the form: {e}"

    return render_template('Booking Page 2.html', booking_id=booking_id)


# Route to show success page
@app.route('/success')
def Success():
    return render_template('Booking Page 3.html')

# Route to show homepage
@app.route('/home')
def home():
    return render_template('Home Page.html')

if __name__ == '__main__':
    BookingTable()  # Initialize the Bookings table
    BookingForm()   # Initialize the Form table
    app.run(debug=True)