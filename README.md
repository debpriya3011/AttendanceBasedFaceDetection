Facial Recognition-Based Attendance System
Overview
This project is a Facial Recognition-Based Attendance System that leverages data science and machine learning to automate attendance tracking. The application captures and analyzes facial data to offer a seamless, contactless, and accurate attendance solution. The core technologies used in this application include the dlib library for facial recognition, PyQt5 for the user interface, SQL Server for database management, and Twilio for SMS notifications.

Features
Face Registration: Register users' faces by capturing facial features through a webcam. Extracts unique face descriptors and stores them in the database with the user's ID, name, and phone number.
Face Deletion: Allows administrators to remove registered faces from the database.
Automated Attendance Logging: Continuously monitors video feeds, detects and recognizes faces, logs attendance, and sends confirmation messages via SMS.
Analytics and Reporting: Provides insightful attendance data through visual tools like bar graphs.
Export to Excel: Facilitates exporting attendance data to Excel for further analysis and record-keeping.
Technologies Used
dlib: High-accuracy facial detection and recognition.
PyQt5: Clean and intuitive user interface.
SQL Server: Efficient database management.
Twilio API: Sends real-time attendance confirmation messages.
OpenCV: Captures and processes video frames from a webcam.
Geocoder: Retrieves the geographical location of the user.
