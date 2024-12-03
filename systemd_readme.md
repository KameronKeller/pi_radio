You can use `systemd` to run your Flask app as a service on your Raspberry Pi. This way, it will start automatically on boot and keep running even if your SSH session closes.

Here are the steps:

1. **Create a systemd service file:**

   Create a new service file for your Flask app. Open a terminal and run:

   ```sh
   sudo nano /etc/systemd/system/flask_app.service
   ```

2. **Add the following content to the service file:**

   ```ini
   [Unit]
   Description=Flask App
   After=network.target

   [Service]
   User=pi
   WorkingDirectory=/path/to/your/app
   ExecStart=/usr/bin/python3 /path/to/your/app/app.py
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

   Replace `/path/to/your/app` with the actual path to your Flask app directory.

3. **Reload systemd to recognize the new service:**

   ```sh
   sudo systemctl daemon-reload
   ```

4. **Start the Flask app service:**

   ```sh
   sudo systemctl start flask_app
   ```

5. **Enable the service to start on boot:**

   ```sh
   sudo systemctl enable flask_app
   ```

6. **Check the status of the service:**

   ```sh
   sudo systemctl status flask_app
   ```

This will ensure that your Flask app runs as a service and continues running even if your SSH session closes.
