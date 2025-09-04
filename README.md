# EZ-Route

A modern, intuitive, and feature-rich desktop GUI for managing your home router. Say goodbye to clunky web interfaces!

---

## About The Project

This project was born out of frustration with the default, often slow and confusing, web interfaces that come with most consumer routers. EZ-Route provides a clean, responsive, and powerful native application to monitor and configure your network with ease.

Our goal is to make network management accessible and straightforward for everyone, from casual users to power users.


*A glimpse of the main dashboard.*

### Key Features

* **Real-time Dashboard:** Monitor upload/download speeds, CPU/RAM usage, and system uptime at a glance.
* **Connected Devices:** View all connected clients, their IP/MAC addresses, connection type, and signal strength.
* **WiFi Management:** Easily change your SSID, password, channel, and security settings for all bands (2.4GHz / 5GHz).
* **Port Forwarding:** A simple interface to create and manage port forwarding rules.
* **System Actions:** Reboot or reset your router directly from the app.
* **Modern UI:** A sleek and responsive interface with light and dark modes. 

---

## Built With

This project is built with a modern tech stack to ensure it's fast, reliable, and cross-platform.

* **Framework:** [Electron, Tauri, Qt]
* **Frontend:** [React, Vue.js, Svelte, plain HTML/CSS/JS]
* **Backend/Router Communication:** [Node.js, Python with libraries like Paramiko, Netmiko(for SSH) or Requests]
* **Styling:** [Tailwind CSS, Material-UI, CSS Modules]

---

## Getting Started

Follow these steps to get a local copy up and running.

### Prerequisites

Make sure you have the following installed:
* **Node.js:** `v18.x` or higher
    ```sh
    node --version
    ```
* **npm (Node Package Manager)**
    ```sh
    npm --version
    ```
### Installation

1.  **Clone the repository:**
    ```sh
    git clone [https://github.com/](https://github.com/)[Your-GitHub-Username]/[Your-Repo-Name].git
    ```
2.  **Navigate to the project directory:**
    ```sh
    cd [Your-Repo-Name]
    ```
3.  **Install dependencies:**
    ```sh
    npm install
    ```
    4.  **Launch the application:**
    ```sh
    npm start
    ```

### Configuration

Before first use, you may need to configure the connection to your router.

1.  Create a `.env` file in the root directory by copying the example file:
    ```sh
    cp .env.example .env
    ```
2.  Edit the `.env` file with your router's details:
    ```
    ROUTER_IP=192.168.1.1
    ROUTER_USERNAME=admin
    ROUTER_PASSWORD=[Your Router Password]
    ```
    **Note:** Storing passwords in plain text is not secure. This method is for local development only.

---

## Usage

After launching the application, it will attempt to connect to the router IP specified in your configuration. The main dashboard will populate with real-time data. Navigate through the sidebar to access different features like WiFi settings, connected devices, and more.

---

## Contributing

Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".

1.  **Fork** the Project
2.  Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3.  Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4.  Push to the Branch (`git push origin feature/AmazingFeature`)
5.  Open a **Pull Request**

Don't forget to give the project a star! Thanks again!

---

## Contact

[Zaid Dhanse] - [dhansezaid019@example.com]

Project Link: [https://github.com/[jaze_019]/[EZ-Route]](https://github.com/[jaze_019]/[EZ-Route])
