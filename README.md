# 2025sp-hexapolo

## Table of Contents

- [Project Overview](#project-overview)
- [Features](#features)
- [Hardware Requirements](#hardware-requirements)
- [Software Requirements](#software-requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)

## Project Overview

The Hexapolo Bot is a six-legged robot that can find and follow a person by listening to their
voice and looking at them. It starts by saying “Marco” and waits for someone to reply “Polo.”
When it hears the reply, the robot uses four microphones to figure out which direction the sound
came from. Then, it turns to face that direction and checks with its camera if a person is there.
If it sees someone, it walks toward them and stops when it is about one meter away. After that,
the robot will follow the person as they move.

The project’s goal is to combine sound detection, camera vision, and motor control so the robot
can interact with people. The robot will also have optional features, like working in a noisy room
or avoiding obstacles using a lidar scanner. The work is divided into small steps to make sure
each part works well before moving to the next.

## Features

- **Keyword Detection:** The robot will listen for the word “Polo” and react when it hears it.
- **Sound Direction Estimation:** It will use four microphones and a time difference of arrival
  (TDoA) method to figure out which direction the sound came from.
- **Turning Toward the Sound:** After detecting the direction of the sound, the robot will rotate
  to face that direction.
- **Visual Detection:** The robot will use its camera to check if there is a person in front of it.
- **Walking Toward the Person:** The robot will move toward the person and stop when it is
  about 50 cm away.

## Hardware Requirements

### Computer

- **Raspberry Pi 1**

  Note : none of our scripts were tested on any Raspberry Pi other than RPi1. However, because of good backward compatibility, all technologies tested on RPi1 should work on any next iteration of the board. Furthermore, you might encounter a few difficulties linked to the limited computing capabilities of the RP1. Using a more recent iteration of a Raspberry Pi such as RPi4 will definitely make the reproducability process much easier.

### Power Source

- **2S 7.4V LiPo battery** (e.g. 2S 7.4V lipo 1100mAh 15C with xt60 connector)
- **DC-DC buck converter** (e.g. WaveShare 6-36V to 5V/3.3V 4A DC-DC buck step down converter)

### Sensors

- **Mic Array** (e.g. ReSpeaker Mic Array v2.0)
- **esp32 Camera** (AI thinker esp 32-cam)

### Sound Output & Speaker

- **Buzzer** (e.g. Purecrea Piezo buzzer active)
- **Speaker**

For our implementation, we stripped out both the speaker and the amplifer from an unbranded speaker. In the same way, you could use whatever speaker with a jack plug you want. Note that the whole build is quite heavy proportionally to the motors, choose your speaker carefully, the lighter the better. It's in the choice of this component that we decided to save some weight, you might also find it a good lead.

### Actuators

- **2x 300rpm 6V n20 motor** (200rpm motors would also work)
- **1.2A DC Motor Driver** (e.g. DFRobot Fermion TB6612FNG 2x1.2A DC Motor Driver)
- **Battery Protection Board** (e.g. 8.4V 2S 20A Lithium Battery Protection BMS Protection Board)

### Mechanical Components

- **3x 8mm wide ball bearings**

### Electrical Interfaces

- **Electrical Switch**
- **USB-A to Micro-USB cable**
- **USB-A to Mini-USB cable**

You might the sum of all the cables' and wires' weight heavy for the motors to move with the rest of the build. We suggest that you cut them short and solder the wires inside.

## Software Requirements

- [List the software dependencies, e.g.:]
  - Python 3.9+
  - RPi.GPIO
  - NumPy
  - OpenCV (if applicable)
  - [Other libraries]

---

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/2025sp-hexapolo.git
   cd 2025sp-hexapolo
   ```
