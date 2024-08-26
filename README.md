# FrameTV Image Gallery Control

This web application allows you to control the art mode of a Samsung FrameTV. You can set specific images, start randomization with adjustable intervals, and view the currently set image, all through an intuitive and aesthetically pleasing interface.

## Features

- **Set Image**: Choose an image from the gallery and set it as the current display on your FrameTV.
- **Randomize**: Automatically change the display image at set intervals.
- **Current Image Display**: Preview the currently set image with a countdown timer showing when the next image will be set.
- **IP Configuration**: Easily set and update the IP address of your FrameTV.

## Prerequisites

- **Python 3.6+**
- **Flask**: The application is built using the Flask framework.
- **APScheduler**: Used for scheduling the randomization of images.
- **Docker**: Optional, for containerized deployment.

## Installation

### Local Setup

1. **Clone the Repository**:
    ```bash
    git clone https://github.com/yourusername/frametv-control.git
    cd frametv-control
    ```

2. **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3. **Run the Application**:
    ```bash
    python app.py
    ```

4. **Access the Application**:
   Open your browser and go to `http://localhost:5000`.

### Docker Setup

1. **Build the Docker Image**:
    ```bash
    docker build -t frametv-control .
    ```

2. **Run the Docker Container**:
    ```bash
    docker run -d -p 5000:5000 -e FRAMETV_IP=192.168.x.x frametv-control
    ```
    Replace `192.168.x.x` with the IP address of your FrameTV.

3. **Access the Application**:
   Open your browser and go to `http://localhost:5000`.

## Environment Variables

- **FRAMETV_IP**: The IP address of your Samsung FrameTV. This must be set when running the application in Docker.

## Usage

1. **Set the FrameTV IP**:
   - Enter the IP address of your FrameTV in the provided input field and click "Set FrameTV IP".
   
2. **Set an Image**:
   - Click on any image in the gallery and then click the "Set Image" button to display it on your FrameTV.

3. **Start Randomization**:
   - Select an interval from the dropdown and click "Randomize" to start changing the images automatically.

4. **Monitor Current Image**:
   - The top-left corner of the interface shows the currently set image and a countdown timer until the next change.

## Contributing

Feel free to fork this repository and submit pull requests. All contributions are welcome!

## License

This project is licensed under the MIT License.
