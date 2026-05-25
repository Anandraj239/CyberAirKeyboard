# Cyber Air Keyboard ⌨️

Cyber Air Keyboard is a next-generation, computer-vision-based virtual keyboard that enables you to type effortlessly in mid-air using your webcam. Built with a focus on speed, accuracy, and highly responsive user feedback, this project eliminates the need for physical hardware altogether.

Developed by [Anandraj239](https://github.com/Anandraj239).
 
## Key Features
* **Advanced Dual-Hand Tracking**: Leveraging Google's MediaPipe, the system tracks multiple hands simultaneously for rapid typing.
* **Precision Pinch-to-Click**: Avoids misclicks by maintaining a strict state machine calculating real-time hand scalability factors. Clicks register robustly between the thumb and index finger.
* **Cyber Aesthetic Interface**: A polished, semi-transparent neon UI written natively in OpenCV with dynamic visual feedback loops.
* **Zero-Latency Processing**: Operates entirely offline with a lightweight footprint.

## Installation & Setup

It is highly recommended to run this project in a **Python 3.11** or **3.12** environment due to specific `mediapipe` Windows dependencies.

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Anandraj239/CyberAirKeyboard.git
   cd CyberAirKeyboard
   ```

2. **Create an isolated Virtual Environment:**
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Launch the Keyboard:**
   ```bash
   python air_keyboard.py
   ```
   *For ease of access on Windows, a `Run Air Keyboard.bat` script is included.*

## Usage Instructions
Simply stand back, face your webcam, and hover over keys using the tip of your **Index finger**. To register a keystroke, clearly pinch your **Thumb and Index finger** together. The buffer responds to standard alphabet inputs alongside Space, Return, Backspace, and Clear keys.   

Press `ESC` to shut down the interface.
