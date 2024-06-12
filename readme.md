# TextToPolly

## Description
TextToPolly is a desktop application that transforms text into spoken audio using AWS Polly. Built with PyQt5, this app offers a user-friendly interface to enter text, select voices, adjust speech speed, and directly output audio. It leverages AWS Polly to deliver high-quality voice synthesis.

## Key Features
- **Text Input**: Users can type or paste text into a text box.
- **Voice Selection**: Multiple voice options are available.
- **Speed Adjustment**: Users can adjust the speed of the speech.
- **Audio Playback**: Integrates with Pygame for audio playback.
- **Credential Management**: Update AWS credentials directly within the app.

## Technologies Used
- **PyQt5**: For the graphical user interface.
- **AWS Polly**: For text-to-speech conversion.
- **Pygame**: For handling audio playback.
- **Python**: The application is written in Python.

## System Requirements
- Python 3.x
- PyQt5
- Boto3
- Pygame
- An active AWS account with Polly access

## Installation and Setup
1. Install required Python packages:
   ```bash
   pip install PyQt5 boto3 pygame
 2. Configure AWS credentials:
   - Ensure AWS credentials (`aws_access_key_id`, `aws_secret_access_key`) are set either through the application interface or within a `polly_credentials.txt` file in the project directory.

3. Running the Application:
   ```bash
   python text_to_polly.py

## How to Contribute
- **Feature Requests**: Open an issue with the tag "feature request".
- **Bug Reports**: Open an issue detailing the bug, how to reproduce it, and any relevant logs.
- **Pull Requests**: Contributions are welcome! Please open pull requests for new features or bug fixes.

## Contact
For support or to contribute to the project, please contact tobi@mauksch.info.
