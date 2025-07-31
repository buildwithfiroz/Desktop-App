<h2 align="left" style="display: flex; align-items: center;">
    CRM Login Desktop App
</h2>


This ***Desktop application*** is designed to streamline the login process for employees accessing the **Company CRM**, making it quicker and more efficient. Additionally, it provides a smart solution for time tracking, ensuring that employees never forget to clock in, thus improving both user experience and administrative tasks.


> [!Tip] <h4>Key Features</h4>
>
> - ***Faster Login***: Achieves login times of 300-500ms, much faster than the typical
700-900ms
> - ***One-time Login***: After the first login, employees stay logged in with the
"Remember Me" option.
> - ***Employee Data Sync***: Fetches employee info (name, position, etc.) directly from
the API.
> - ***Automatic Startup***: The app runs automatically on system boot for seamless login



<br>

![Python](https://img.shields.io/badge/Python-3.9-blue?style=for-the-badge&logo=python&logoColor=yellow) &nbsp; &nbsp;
![JSON](https://img.shields.io/badge/JSON-Enabled-lightgray?style=for-the-badge&logo=json&logoColor=white) &nbsp; &nbsp;
![API](https://img.shields.io/badge/API-Integrated-lightblue?style=for-the-badge&logo=api&logoColor=white) &nbsp; &nbsp;
![Kivy](https://img.shields.io/badge/Kivy-Framework-black?style=for-the-badge&logo=kivy&logoColor=green) &nbsp; &nbsp;
![KivyMD](https://img.shields.io/badge/KivyMD-UI%20Toolkit-ff69b4?style=for-the-badge&logo=kivy&logoColor=white) &nbsp; &nbsp;
![Windows](https://img.shields.io/badge/Windows-OS-blue?style=for-the-badge&logo=windows&logoColor=white) &nbsp; &nbsp;
![macOS](https://img.shields.io/badge/macOS-OS-lightgray?style=for-the-badge&logo=apple&logoColor=black) &nbsp; &nbsp;
![Linux](https://img.shields.io/badge/Linux-OS-orange?style=for-the-badge&logo=linux&logoColor=black) &nbsp; &nbsp;

<br> 


<p align="left">
  <img src="src/git/Desktop-login.png" alt="Desktop View" width="100%" />
</p>

<br> 

<br>



> [!IMPORTANT]
>
> ### Why I Built This
> Employees at my company frequently forgot to clock in, leading to errors in time tracking and even salary deductions.
>
> - Employees often forgot to clock in, requiring manual adjustments by admins
> - Time tracking was prone to mistakes and salary issues 
> - The login process was slow , Open chrome and login and then press clock-in  
> - Employees had to log in every time they started their system, creating extra effort
>
> This led to inefficiency, increased administrative workload, and a frustrating user experience.
>
> ---
> 
> ### How I Solved the Problem
>
> So I built CRM Login Enhancer — a desktop app that:
> - Optimizes login times to ***300-500ms***, making it faster and more efficient
> - Remembers login credentials for seamless access after the first login
> - Runs automatically at system startup, ensuring users are always ready to clock in  
> - Syncs employee data (name, position, etc.) directly from the company’s CRM AP
>
> It's designed for both tech-savvy employees and non-technical users — providing an easy-to-use interface that speeds up login, reduces administrative tasks, and ensures accurate time tracking for everyone



<br>



##  How It Works: Step-by-Step User Guide

1. **Launch the App**  
   - Upon starting the app, it will automatically run in the background on system boot.
   - You will see a login window prompting you to enter your Username and Password.
   - The login process may take 300-500ms, much faster than typical APIs.

    <br>
   <img src="src/git/Desktop-login.png" alt="Desktop View" width="50%" />
     <br>

2. **View the Success Window**  

   - After entering your Username and Password, click Login.
   - If your credentials are correct, you will see a success message confirming the login.

    <br>
   <img src="src/git/output-login.png" alt="Desktop View" width="50%" />
    <br>

3. **No Need for Re-login**  
   - The next time you launch the app, your credentials will be auto-filled.
   - You will no longer need to enter your Username or Password. Simply click Clock In to start tracking your time.

    <br>
   <img src="src/git/clock-in.png" alt="Desktop View" width="30%" />
    <br>



## 5. Summary  
Watch this quick video to understand the simple workflow and how the app makes login and time tracking effortless.


https://github.com/user-attachments/assets/9b7a71e2-a9ad-4ec1-88ee-ab9846043489




<br>
<br>

# Login Performance Comparison

## 🚀 CRM Enhancer vs. Postman

| Feature              | CRM Login Enhancer                                                                 | Traditional (Postman/API)                                                              |
|----------------------|-------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------|
| **Login Speed**      | ⏱️ 300–500ms                                                                       | 🕒 800–1500ms seconds                                                                    |
| **Login Screenshot** | <img src="src/git/benchmark-inhouse.png" width="100%"/>                             | <img src="src/git/benchmark-postmen.png" width="60%"/>                                  |

<br>

<br>


> [!NOTE]
>
> Follow these steps to get started - 
>
> **Step 1:**  
> Clone the repository  
> ```bash
> git clone https://github.com/buildwithfiroz/Desktop-App.git
> ```
>
> **Step 2:**  
> Change directory into the project folder  
> ```bash
> cd Desktop-App
> ```
>
> **Step 3:**  
> Create a Python virtual environment  
> ```bash
> python3 -m venv myenv
> ```
>
> **Step 4:**  
> Activate the virtual environment  
> - On macOS/Linux:  
> ```bash
> source myenv/bin/activate
> ```
> - On Windows (PowerShell):  
> ```powershell
> .\myenv\Scripts\Activate.ps1
> ```
>
> **Step 5:**  
> Install required dependencies  
> ```bash
> pip3 install -r requirements.txt
> ```
>
> **Step 6:**  
> Run the app  
> ```bash
> python3 login.py
> ```
>
> Now enjoy using Desktop app, or customize it further as needed!
>
>


<br>
<br>

## 👨‍💻 Author - Contact Information
---
This project is proudly built and maintained by [@buildwithfiroz](https://github.com/buildwithfiroz).

If you found this useful, consider giving it a ***⭐️ on GitHub*** or contributing to improve it further!

<br>

<p align="left">
  <a href="https://github.com/buildwithfiroz">
    <img width='220' src="https://img.shields.io/badge/GitHub-@buildwithfiroz-181717?logo=github&style=for-the-badge" alt="GitHub" /></a> &nbsp;
  <a href="mailto:buildbyfiroz@icloud.com">
    <img width='250' src="https://img.shields.io/badge/Email-buildbyfiroz@icloud.com-blue?logo=gmail&style=for-the-badge" alt="Email" /></a>
</p>

---


<br>

<p align="center"><b>Made with ❤️ by Firoz</b></p>

