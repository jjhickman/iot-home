FROM jjhickman/opencv-python:headless
WORKDIR /security-cam

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .
CMD ["python3", "security-cam.py"]
