# Face Recognition and Registration System - Task 3 MLCOE

This is a simple face recognition and registration system implemented using Flask, OpenCV, and face_recognition library. The system allows users to register, log in, and verify their identity using facial recognition.

## Features

- **User Registration:** Users can register by providing a username, email, and password.

- **User Login:** Registered users can log in using their username, email, and password.

- **User Verification:** After logging in, users can capture an image to verify their identity. The system compares the captured image with the registered face image using face recognition.

- **Camera Feed:** Users can access their camera feed and apply various filters such as grayscale, negative, and face detection.

## Prerequisites

- Python
- Flask
- OpenCV
- face_recognition library

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/lakshya324/MLCOE-Task-3.git
   ```

2. Install the required dependencies:

   ```bash
   pip install Flask Flask-SQLAlchemy opencv-python face_recognition
   ```

3. Run the application:

   ```bash
   python app.py
   ```

4. Open your web browser and navigate to [http://localhost:5000](http://localhost:5000) to access the application.

## Usage

1. **Registration:**
   - Visit the homepage and register by providing a username, email, and password.
   - After registration, proceed to the camera feed to capture your face for verification.

2. **Login:**
   - Log in using your username, email, and password.

3. **Verification:**
   - After logging in, click the "Capture" button to capture an image.
   - The system will compare the captured image with the registered face for verification.

4. **Camera Feed:**
   - Access your camera feed by navigating to the camera page.
   - Apply filters such as grayscale, negative, or face detection.

5. **Logout:**
   - Click on the "Logout" button to log out of your account.

## Folder Structure

- `static/`: Contains static files, including user and captured images.
- `templates/`: Contains HTML templates for rendering web pages.
- `saved_model/`: Contains the pre-trained face detection model.

## Author

Lakshya Sharma

## Acknowledgments

- [OpenCV](https://opencv.org/)
- [face_recognition](https://github.com/ageitgey/face_recognition)
- [Flask](https://flask.palletsprojects.com/)
