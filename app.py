import sys
import cv2
import numpy as np
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QPushButton,
    QDialog, QLineEdit, QVBoxLayout, QListWidget, QMessageBox,QFileDialog
)
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer, Qt, QDateTime, QDate, QTime
import dlib
from twilio.rest import Client
import matplotlib.pyplot as plt
import pyodbc
import geocoder
import pandas as pd


class DeleteFaceDialog(QDialog):
    def __init__(self, known_names, conn, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Delete Faces")
        self.known_names = known_names
        self.conn = conn

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        self.face_list_widget = QListWidget(self)
        layout.addWidget(self.face_list_widget)

        self.delete_button = QPushButton("Delete Selected Faces", self)
        self.delete_button.clicked.connect(self.delete_selected_faces)
        layout.addWidget(self.delete_button)

        self.populate_face_list()

    def populate_face_list(self):
        self.face_list_widget.clear()
        for name in self.known_names:
            self.face_list_widget.addItem(name)

    def delete_selected_faces(self):
        selected_items = self.face_list_widget.selectedItems()
        if not selected_items:
            return

        selected_names = [item.text() for item in selected_items]
        for name in selected_names:
            self.delete_face_from_database(name)
            self.known_names = [n for n in self.known_names if n != name]

        self.populate_face_list()

        # Call refresh_face_display directly on the parent (FaceRecognitionApp instance)
        if isinstance(self.parent(), FaceRecognitionApp):
            self.parent().refresh_face_display()

        QMessageBox.information(self, "Faces Deleted", "Selected faces deleted successfully.")

        self.accept()  # Close the dialog after deletion

    def delete_face_from_database(self, name):
        query = "DELETE FROM students WHERE name = ?"
        self.conn.execute(query, (name,))
        self.conn.commit()

        print(f"Deleted face: {name} from database")


class FaceRegistrationDialog(QDialog):
    def __init__(self, detector, face_rec, known_encodings, known_names, conn):
        super().__init__()
        self.setWindowTitle("Face Registration")
        self.detector = detector
        self.face_rec = face_rec
        self.known_encodings = known_encodings
        self.known_names = known_names
        self.conn = conn

        self.shape_predictor = dlib.shape_predictor("C:/Users/debpr/Downloads/shape_predictor_68_face_landmarks.dat/shape_predictor_68_face_landmarks.dat")

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        self.id_input = QLineEdit(self)
        self.id_input.setPlaceholderText("Enter ID")
        layout.addWidget(self.id_input)

        self.name_input = QLineEdit(self)
        self.name_input.setPlaceholderText("Enter Name")
        layout.addWidget(self.name_input)

        self.phone_input = QLineEdit(self)
        self.phone_input.setPlaceholderText("Enter Phone Number")
        layout.addWidget(self.phone_input)

        self.register_button = QPushButton("Register", self)
        self.register_button.clicked.connect(self.register_face)
        layout.addWidget(self.register_button)

    def register_face(self):
        id_val = self.id_input.text().strip()
        name = self.name_input.text().strip()
        phone_number = self.phone_input.text().strip()

        if id_val and name and phone_number:
            # cap = cv2.VideoCapture(0)
            cap = cv2.VideoCapture(cv2.CAP_DSHOW, 0)  # Use DirectShow backend

            ret, frame = cap.read()

            if ret:
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                face_locations = self.detector(rgb_frame, 0)
                
                if face_locations:
                    shape = self.shape_predictor(rgb_frame, face_locations[0])
                    face_enc = self.face_rec.compute_face_descriptor(rgb_frame, shape)

                    # Append new face encoding to known_encodings
                    self.known_encodings = np.vstack([self.known_encodings, face_enc])

                    # Append new name to known_names
                    new_names_array = np.array([name])  # Create a new NumPy array with the new name
                    self.known_names = np.concatenate([self.known_names, new_names_array])

                    # Save updated encodings and names to files
                    np.save("known_encodings.npy", self.known_encodings)
                    np.save("known_names.npy", self.known_names)

                    # Insert new record into database
                    self.conn.execute("INSERT INTO students (id, name, phone_number) VALUES (?, ?, ?)",
                                    (id_val, name, phone_number))
                    self.conn.commit()

                    print(f"Registered new face for {name} with ID: {id_val} and Phone: {phone_number}")
                else:
                    print("No face detected for registration.")
            else:
                print("Error capturing frame from the video source.")
        else:
            print("Please enter valid ID, Name, and Phone Number.")

        # Release video capture resources
        cap.release()

        self.accept()  # Close the dialog after registration



class FaceRecognitionApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Attendance Detection App")
        self.setGeometry(100, 100, 800, 600)

        self.init_ui()

    def init_ui(self):
        self.label = QLabel(self)
        self.label.setGeometry(10, 10, 640, 480)

        self.face_list_widget = QListWidget(self)  # Create the QListWidget
        layout = QVBoxLayout(self)
        layout.addWidget(self.face_list_widget)

        self.start_button = QPushButton("Start", self)
        self.start_button.setGeometry(680, 10, 100, 30)
        self.start_button.setStyleSheet("background-color: lightblue; color: black; font-weight: bold; border-radius: 15px;")
        self.start_button.clicked.connect(self.start_recognition)

        self.stop_button = QPushButton("Stop", self)
        self.stop_button.setGeometry(680, 50, 100, 30)
        self.stop_button.setStyleSheet("background-color: lightcoral; color: black; font-weight: bold; border-radius: 15px;")
        self.stop_button.clicked.connect(self.stop_recognition)
        self.stop_button.setEnabled(False)

        self.register_button = QPushButton("Register Face", self)
        self.register_button.setGeometry(680, 90, 100, 30)
        self.register_button.setStyleSheet("background-color: lightgreen; color: black; font-weight: bold; border-radius: 15px;")
        self.register_button.clicked.connect(self.open_registration_dialog)

        self.delete_face_button = QPushButton("Delete Faces", self)
        self.delete_face_button.setGeometry(680, 130, 100, 30)
        self.delete_face_button.setStyleSheet("background-color: lightpink; color: black; font-weight: bold; border-radius: 15px;")
        self.delete_face_button.clicked.connect(self.open_delete_face_dialog)

        # self.update_face_button = QPushButton("Update Face Display", self)
        # self.update_face_button.setGeometry(680, 170, 100, 30)
        # self.update_face_button.setStyleSheet("background-color: lightyellow; color: black; font-weight: bold;")
        # self.update_face_button.clicked.connect(self.update_face_display)

        self.analytics_button = QPushButton("View Analytics", self)
        self.analytics_button.setGeometry(680, 170, 100, 30)
        self.analytics_button.setStyleSheet("background-color: lightblue; color: black; font-weight: bold; border-radius: 15px;")
        self.analytics_button.clicked.connect(self.view_analytics)
        
        self.export_button = QPushButton("Export to Excel", self)  # New button for exporting to Excel
        self.export_button.setGeometry(680, 210, 100, 30)
        self.export_button.setStyleSheet("background-color: lightyellow; color: black; font-weight: bold; border-radius: 15px;")
        self.export_button.clicked.connect(self.export_to_excel)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.detect_faces)

        self.cap = cv2.VideoCapture(0)

        # Database connection
        self.conn_str = "DRIVER={SQL Server};SERVER=LAPTOP-5O1ATMJ0\\SQLEXPRESS;DATABASE=phone;Trusted_Connection=yes"
        self.conn = pyodbc.connect(self.conn_str)

        # Face detection and recognition models
        self.detector = dlib.get_frontal_face_detector()
        self.shape_predictor = dlib.shape_predictor("C:/Users/debpr/Downloads/shape_predictor_68_face_landmarks.dat/shape_predictor_68_face_landmarks.dat")
        self.face_rec = dlib.face_recognition_model_v1("C:/Users/debpr/Downloads/dlib_face_recognition_resnet_model_v1.dat")

        # Load known encodings and names
        self.known_encodings = np.load("known_encodings.npy", allow_pickle=True)
        self.known_names = np.load("known_names.npy", allow_pickle=True)

        self.last_sent_time = {}

    def start_recognition(self):
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.timer.start(100)  # Update every 100 milliseconds

    def stop_recognition(self):
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.timer.stop()

    def open_registration_dialog(self):
        dialog = FaceRegistrationDialog(self.detector, self.face_rec, self.known_encodings, self.known_names, self.conn)
        dialog.exec_()
        

    def refresh_face_display(self):
        # Fetch the latest list of known names from the database
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT name FROM students")
            updated_names = [row.name for row in cursor.fetchall()]

            # Update the known_names attribute with the updated names
            self.known_names = updated_names

            # Clear and repopulate the face list widget with the updated names
            self.populate_face_list()

            QMessageBox.information(self, "Refresh", "Face list refreshed successfully.")

        except pyodbc.Error as e:
            QMessageBox.warning(self, "Error", f"Error refreshing face list: {e}")
    

    def open_delete_face_dialog(self):
        dialog = DeleteFaceDialog(self.known_names, self.conn, parent=self)
        dialog.exec_()

    def detect_faces(self):
        ret, frame = self.cap.read()
        if not ret:
            return

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        faces = self.detector(rgb_frame, 0)

        for face in faces:
            # Get the coordinates of the face bounding box
            left = face.left()
            top = face.top()
            right = face.right()
            bottom = face.bottom()

            # Draw a rectangle around the face
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

            # Perform face recognition and attendance logging as before
            shape = self.shape_predictor(rgb_frame, face)
            face_encoding = self.face_rec.compute_face_descriptor(rgb_frame, shape)
            distances = np.linalg.norm(self.known_encodings - face_encoding, axis=1)
            min_distance = np.min(distances)
            min_index = np.argmin(distances)

            if min_distance < 0.5 and min_index < len(self.known_names):
                recognized_name = self.known_names[min_index]
                phone_number = self.get_phone_number(recognized_name)
                if phone_number and self.can_send_attendance(recognized_name):
                    self.send_attendance_confirmation(recognized_name, phone_number)
            else:
                recognized_name = "Unknown Person"

            cv2.putText(frame, f"{recognized_name} (ID: {min_index})", (left, bottom + 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        self.display_frame(frame)



    def display_frame(self, frame):
        bgr_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        h, w, _ = frame.shape
        img = QImage(frame.data, w, h, 3 * w, QImage.Format_BGR888)
        pixmap = QPixmap.fromImage(img)
        self.label.setPixmap(pixmap.scaled(self.label.size(), Qt.KeepAspectRatio))

    def view_analytics(self):
        # Perform analytics and plot attendance graph
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT date, COUNT(*) FROM attendance_register GROUP BY date")
            result = cursor.fetchall()

            dates = [row.date for row in result]
            counts = [row[1] for row in result]

            plt.figure(figsize=(10, 6))
            plt.bar(dates, counts, color='skyblue')
            plt.xlabel('Date')
            plt.ylabel('Attendance Count')
            plt.title('Daily Attendance Analytics')
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.show()

        except pyodbc.Error as e:
            QMessageBox.warning(self, "Error", f"Error retrieving attendance data: {e}")  


    def export_to_excel(self):
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM attendance_register")
            data = cursor.fetchall()
            df = pd.DataFrame(data)  # Create DataFrame without specifying columns

            file_path, _ = QFileDialog.getSaveFileName(self, "Save Excel File", "", "Excel files (*.xlsx)")

            if file_path:
                df.to_excel(file_path, index=False)
                QMessageBox.information(self, "Export", "Data exported to Excel successfully.")

        except pyodbc.Error as e:
            QMessageBox.warning(self, "Error", f"Error exporting data to Excel: {e}")


    def get_phone_number(self, name):
        query = "SELECT phone_number FROM students WHERE name = ?"
        result = self.conn.execute(query, (name,)).fetchone()
        if result:
            phone_number = result[0]
            if not phone_number.startswith('+'):
                phone_number = '+' + phone_number
            return phone_number
        else:
            return None

    def can_send_attendance(self, name):
        current_time = QDateTime.currentDateTime()

        if name not in self.last_sent_time:
            self.last_sent_time[name] = current_time
            return True
        else:
            last_time_sent = self.last_sent_time[name]
            elapsed_seconds = last_time_sent.secsTo(current_time)
            if elapsed_seconds >= 8 * 3600:
                self.last_sent_time[name] = current_time
                return True
            else:
                return False

    def send_attendance_confirmation(self, name, phone_number):
        account_sid = 'ACXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
        auth_token = 'your_auth_token_here'
        from_number = '+12345678901'

        try:
            g = geocoder.ip('me')
            location = g.latlng if g.latlng else None
            location_str = (
                f"Latitude: {location[0]}, Longitude: {location[1]}"
                if location
                else "Location not available"
            )

            # Get the current date in ISO 8601 format (YYYY-MM-DD)
            import datetime
            current_date_iso = datetime.date.today().isoformat()

            message_body = f"Attendance detected for {name}. Welcome, {name}! Location: {location_str}"

            client = Client(account_sid, auth_token)
            message = client.messages.create(
                body=message_body,
                from_=from_number,
                to=phone_number
            )

            self.last_sent_time[name] = QDateTime.currentDateTime()
            print(f"Attendance Message sent successfully to {phone_number} ({name}): {message.sid} Location: {location_str}")

            if location:
                latitude, longitude = location
                self.conn.execute(
                    "INSERT INTO attendance_register (date, time, phone_number, name, latitude, longitude) VALUES (?, ?, ?, ?, ?, ?)",
                    (
                        current_date_iso,  # Use the formatted date
                        QTime.currentTime().toString(Qt.ISODate),
                        phone_number,
                        name,
                        latitude,
                        longitude
                    )
                )
                self.conn.commit()

        except Exception as e:
            print(f"Error sending message: {e}")
            print("Failed to send attendance confirmation. Please check your network connection and Twilio settings.")



    def update_face_display(self):
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT name FROM students")
            updated_names = [row.name for row in cursor.fetchall()]
            
            self.known_names = updated_names
            QMessageBox.information(self, "Update", "Face list updated successfully.")
            
        except pyodbc.Error as e:
            QMessageBox.warning(self, "Error", f"Error updating face list: {e}")

        self.parent().refresh_face_display()  # Assuming a method to refresh the display in the parent widget

    def closeEvent(self, event):
        self.cap.release()
        event.accept()

    def populate_face_list(self):
        # Clear existing items in the face list widget
        self.face_list_widget.clear()

        # Add items (known names) to the face list widget
        for name in self.known_names:
            self.face_list_widget.addItem(name)    
    
    

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = FaceRecognitionApp()
    window.show()
    sys.exit(app.exec_())
