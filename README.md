Overview :
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


Setup and Installation
Clone the Repository:

bash
Copy code
git clone https://github.com/yourusername/attendance-detection-app.git
cd attendance-detection-app
Install Dependencies:

bash
Copy code
pip install -r requirements.txt
Configure Twilio:
Replace the placeholder values in the send_attendance_confirmation function with your Twilio credentials.

python
Copy code
account_sid = 'ACXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
auth_token = 'your_auth_token_here'
from_number = '+12345678901'
Run the Application:

bash
Copy code
python app.py
Usage
Register Faces:

Launch the application.
Use the face registration feature to add users by capturing their facial features.
Monitor Attendance:

The application will automatically detect and recognize faces from the video feed.
Attendance logs are updated in real-time, and SMS notifications are sent to registered users.
View Analytics and Export Data:

Access the analytics section to view attendance trends and patterns.
Export the attendance data to Excel for detailed analysis.
Example False Twilio Configuration
For demonstration purposes, you can use the following false Twilio configuration:

python
Copy code
account_sid = 'ACXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
auth_token = 'your_auth_token_here'
from_number = '+12345678901'
Contributing
We welcome contributions to improve this project. Please follow these steps to contribute:

Fork the repository.
Create a new branch for your feature or bug fix.
Commit your changes with a descriptive message.
Push your branch to your forked repository.
Create a pull request to the main branch of this repository.



Acknowledgments
This project uses the dlib library for facial recognition and detection.
PyQt5 is used for the graphical user interface.
Twilio API integration provides SMS notification functionality.
Future Enhancements
Real-Time Reporting: Implement real-time reporting for immediate insights.
Multi-Camera Support: Add support for multiple cameras.
Cloud Integration: Integrate with cloud services for enhanced scalability.


You may get errors like this :
![image](https://github.com/user-attachments/assets/ea38fbd6-5ccc-4daa-9247-8645fca665e2)

To solve:
        You must use Visual Studio to build a python extension on windows.  If you
        are getting this error it means you have not installed Visual C++.  Note
        that there are many flavors of Visual Studio, like Visual Studio for C#
        development.  You need to install Visual Studio for C++.

        STEP 1:
  Download CMake from official website      
        
  ![image](https://github.com/user-attachments/assets/2ace0419-8bd3-46c9-b684-f40002afdd5a)

  pip install cmake 

        STEP 2:
![image](https://github.com/user-attachments/assets/80ec8fea-870d-458a-9371-7a8ea5932515)

  pip install --upgrade pip setuptools

        STEP3:
install VS Build Tools with Desktop Development C++
        ![image](https://github.com/user-attachments/assets/2d1e2156-44db-4932-a6a4-95e49fb9c8e8)

  ![image](https://github.com/user-attachments/assets/9611e8c0-1328-4024-b7d1-e8d706adb80a)



        STEP 4:
Make sure you have added CMake in environment variables

![image](https://github.com/user-attachments/assets/0fd3eeb0-707d-40df-bed4-8fed02cc8457)

        STEP 5:
  Download the Dlib .whl file for the Python version
  
  https://github.com/z-mahmud22/Dlib_Windows_Python3.x
  
        STEP 6:
  change directories to where YOU saved the .whl file      

        STEP 7:
  run pip install [.whl filename (including extension)]      
  
![image](https://github.com/user-attachments/assets/0114bafe-f6ec-4830-9ce9-65876cea3f2b)

        
        

  


