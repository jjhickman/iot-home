# iot-home
DIY Smart Home IoT Solution with Tensorflow Lite and OpenCV

<!-- PROJECT SHIELDS -->
<!--
*** I'm using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->
[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]
[![LinkedIn][linkedin-shield]][linkedin-url]


<!-- PROJECT LOGO -->
<br />
<p align="center">
  <a href="https://github.com/jjhickman/iot-home">
    <img src="images/logo.png" alt="Logo" width="80" height="80">
  </a>

  <h3 align="center">IoT Home</h3>

  <p align="center">
  DIY Smart Home IoT Solution with Tensorflow Lite and OpenCV
    <br />
    <a href="https://github.com/jjhickman/iot-home/docs"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://jjhickman.com/iot-home">View Demo</a>
    ·
    <a href="https://github.com/jjhickman/iot-home/issues">Report Bug</a>
    ·
    <a href="https://github.com/jjhickman/iot-home/issues">Request Feature</a>
  </p>
</p>



<!-- TABLE OF CONTENTS -->
## Table of Contents

* [About the Project](#about-the-project)
  * [Built With](#built-with)
* [Getting Started](#getting-started)
  * [Prerequisites](#prerequisites)
  * [Installation](#installation)
* [Usage](#usage)
* [Roadmap](#roadmap)
* [Contributing](#contributing)
* [License](#license)
* [Contact](#contact)
* [Acknowledgements](#acknowledgements)

<!-- ABOUT THE PROJECT -->
## About The Project

[![Product Name Screen Shot][product-screenshot]](https://jjhickman.com/iot-home)

Words words words

### Built With
This system consists of multiple software components and devices. As such the requirements listed will be respective to each component:

#### IoT Hub
* [Raspberry Pi Cluster](https://www.raspberrypi.org/)
* [Ubuntu](https://ubuntu.com/)
* [Kubernetes / K3S](https://k3s.io/)
* [NGINX](https://www.nginx.com/)
* [Cert-Manager](https://github.com/jetstack/cert-manager)
* [Metal LB](https://metallb.universe.tf/)

##### Interpreter Service
* [Tensorflow / Tensorflow Lite](https://www.tensorflow.org/lite)
* [OpenCV](https://opencv.org/)
* [Keras](https://keras.io/)
* [Python](https://www.python.org/)

##### REST API Service
* [Java](https://www.java.com/en/)
* [Spring](https://spring.io/)
* [MySQL](https://www.mysql.com/)

##### Notification Service
* [JavaScript](https://www.javascript.com/)
* [Node.js](https://nodejs.org/en/)
* [Amazon Web Services - SNS](https://aws.amazon.com/sns/)

##### Upload Service
* [JavaScript](https://www.javascript.com/)
* [Node.js](https://nodejs.org/en/)
* [Amazon Web Services - S3](https://aws.amazon.com/s3/)

#### Motion Detection Security Camera
* [Python](https://www.python.org/)
* [Amazon Web Services - SNS](https://aws.amazon.com/sns/)

#### Voice Assistant
* [Python](https://www.python.org/)

<!-- GETTING STARTED -->
## Getting Started

This is how to setup the project locally. For the cluster, there is a Kubernetes configuration under the iot-hub directory.
To get a local copy up and running follow these simple example steps.

### Installation

1. Clone the repo
```sh
git clone https://github.com/jjhickman/iot-home.git
```


<!-- USAGE EXAMPLES -->
## Usage

Use this space to show useful examples of how a project can be used. Additional screenshots, code examples and demos work well in this space. You may also link to more resources.

_For more examples, please refer to the [Documentation](https://jjhickman.com/iot-home)_



<!-- ROADMAP -->
## Roadmap

See the [open issues](https://github.com/jjhickman/iot-home/issues) for a list of proposed features (and known issues).



<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such an amazing place to be learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE` for more information.

<!-- CONTACT -->
## Contact

Josh Hickman - [@kissmyasimov](https://twitter.com/kissmyasimov) - jjhickman@protonmail.com

Project Link: [https://github.com/jjhickman/iot-home](https://github.com/jjhickman/iot-home)

<!-- ACKNOWLEDGEMENTS -->
## Acknowledgements
* [Andy Sandberg's FaceNet](https://github.com/davidsandberg/facenet)


<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/jjhickman/iot-home.svg?style=flat-square
[contributors-url]: https://github.com/jjhickman/iot-home/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/jjhickman/iot-home.svg?style=flat-square
[forks-url]: https://github.com/jjhickman/iot-home/network/members
[stars-shield]: https://img.shields.io/github/stars/jjhickman/iot-home.svg?style=flat-square
[stars-url]: https://github.com/jjhickman/iot-home/stargazers
[issues-shield]: https://img.shields.io/github/issues/jjhickman/iot-home.svg?style=flat-square
[issues-url]: https://github.com/jjhickman/iot-home/issues
[license-shield]: https://img.shields.io/github/license/jjhickman/iot-home.svg?style=flat-square
[license-url]: https://github.com/jjhickman/iot-home/blob/master/LICENSE.txt
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=flat-square&logo=linkedin&colorB=555
[linkedin-url]: https://linkedin.com/in/joshjh
[product-screenshot]: images/screenshot.png
