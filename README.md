# Employee Time Tracker

Simple File Strcutre

A desktop application for employee time tracking built with Python, Kivy, and KivyMD.

## Features

- User authentication
- Clock in/out functionality
- User profile with photo
- Work hours tracking
- Modern UI with Material Design

## Prerequisites

- Python 3.7 or higher
- pip (Python package manager)
- Git (optional, for cloning the repository)

## Installation

### Windows

1. Clone the repository or download the source code
2. Double-click on `build.bat`
3. The built application will be in the `dist` folder

### macOS/Linux

1. Clone the repository or download the source code
2. Make the build script executable:
   ```bash
   chmod +x build.sh
   ```
3. Run the build script:
   ```bash
   ./build.sh
   ```
4. The built application will be in the `dist` folder

## Configuration

Edit the `.env` file to configure the application:

```
ENDPOINT=your-api-endpoint.com
URL=https://your-api-endpoint.com/api/login
ADMIN_PASS=your_admin_password
```

## Building from Source

1. Create a virtual environment:
   ```bash
   python -m venv myenv
   ```

2. Activate the virtual environment:
   - Windows: `myenv\Scripts\activate`
   - macOS/Linux: `source myenv/bin/activate`

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the application:
   ```bash
   python login.py
   ```

## Building the Executable

### Using PyInstaller

1. Install PyInstaller if you haven't already:
   ```bash
   pip install pyinstaller
   ```

2. Build the executable:
   ```bash
   pyinstaller --clean --noconfirm build.spec
   ```

3. The executable will be in the `dist` folder

## Project Structure

- `login.py` - Main application entry point
- `clock_window.py` - Clock in/out interface
- `notify_popup.py` - Notification popup component
- `build.spec` - PyInstaller configuration
- `requirements.txt` - Python dependencies
- `src/` - Static assets (images, sounds, etc.)
- `.env` - Environment configuration

## License

This project is proprietary software. All rights reserved.

## Support

For support, please contact your system administrator.
