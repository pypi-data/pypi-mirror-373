# MirrorBox 🚀

**A smart, caching proxy for Docker, designed to bypass registry restrictions and accelerate your image pulls.**

MirrorBox is a modern command-line tool that acts as a smart gateway for Docker. It intelligently routes your Docker image requests through the fastest available mirrors, caches images locally for offline access, and seamlessly integrates with your development workflow.

---

## ✨ Key Features

- ✅ **Accelerated Image Pulls:** Automatically benchmarks and selects the fastest, most reliable mirror before every download, dramatically speeding up `docker pull`.
- ✅ **Seamless Docker Compose Integration:** Replace `docker-compose up` with `mirrorbox compose up`. MirrorBox pre-fetches all required images for your services, ensuring your projects start without delay.
- ✅ **Intelligent Local Caching:** Pulled images are automatically cached locally. Subsequent requests are served instantly from your disk, saving bandwidth and enabling offline work.
- ✅ **Full Cache Management:** Simple commands to `list`, `save`, and `remove` cached images.
- ✅ **Configuration Control:** Customize MirrorBox. Set a `priority_mirror` to always use your favorite registry first.
- ✅ **Complete Docker Integration:** List all images currently in your Docker daemon with `list-images`.
- ✅ **Live Monitoring & Reporting:** Get a live dashboard of mirror statuses with `monitor start` and review performance history with `report show`.

---

## 📦 Installation & Quick Start

MirrorBox requires **Python 3.10+**.  
It is strongly recommended to install it inside a **virtual environment** to avoid conflicts with system packages.

### 1️⃣ Create a Virtual Environment
```bash
python3 -m venv venv
```

## 2️⃣ Activate the Environment
```bash
source venv/bin/activate (Linux)
venv\Scripts\activate.bat (Windonws)
```
## 3️⃣ Install MirrorBox
```bash
pip install --upgrade mirrorbox
```
## 🛠️ Usage / Commands
```bash
mirrorbox start
```

---

## ✨ New in v1.0: The Graphical User Interface!

For a more visual and user-friendly experience, you can now launch the MirrorBox desktop application.

Simply run:
```bash
mirrorbox open
```

The GUI allows you to manage all key features of MirrorBox from a beautiful and modern interface.

![MirrorBox GUI](assets/mirrorbox-gui.png)

---


Below is a detailed guide to available commands:
## 1. Basic Mirror & Image Commands
## Check Mirror Status
```bash
mirrorbox list-mirrors
```
## Search for an Image
```bash
mirrorbox search nginx:latest
```
## Pull an Image (Smart Pull)
```bash
mirrorbox pull ubuntu:22.04
```
## List Local Docker Images
```bash
mirrorbox list-images
```

## 2. Docker Compose Integration
```bash
mirrorbox compose up -d --build
```

## 3. Cache Management
## List Cached Images
```bash
mirrorbox cache list
```
## Save an Image to Cache
```bash
mirrorbox cache save httpd:latest
```
## Remove Cached Images
```bash
mirrorbox cache remove httpd-latest.tar nginx-latest.tar
```

## 4. Configuration
## View Current Settings
```bash
mirrorbox config show
```
## Set a Priority Mirror
```bash
mirrorbox config set-priority focker.ir
```
## Unset Priority Mirror
```bash
mirrorbox config unset-priority
```

## 5. Monitoring & Reporting
## Show History Report
```bash
mirrorbox report show --limit 15
```
## Launch Live Dashboard
```bash
mirrorbox monitor start --interval 5
```
## 📄 License
Copyright (c) 2025 Pouya Rezapour.
All Rights Reserved. See the LICENSE file for more details.








