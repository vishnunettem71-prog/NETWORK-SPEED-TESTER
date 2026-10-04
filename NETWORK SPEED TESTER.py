import tkinter as tk
from tkinter import ttk
import urllib.request
import urllib.parse
import time
import threading
import socket
import statistics


class NetworkSpeedTester:

    def __init__(self, root):
        self.root = root
        self.root.title("Network Speed Tester")
        self.root.geometry("800x600")
        self.root.configure(bg="#101820")

        self.testing = False

        self.create_ui()

    def create_ui(self):

        # Title
        title = tk.Label(
            self.root,
            text="NETWORK SPEED TESTER",
            font=("Arial", 26, "bold"),
            fg="#00e5ff",
            bg="#101820"
        )
        title.pack(pady=25)

        subtitle = tk.Label(
            self.root,
            text="Test your Internet connection speed",
            font=("Arial", 12),
            fg="white",
            bg="#101820"
        )
        subtitle.pack()

        # Start button
        self.start_button = tk.Button(
            self.root,
            text="START SPEED TEST",
            font=("Arial", 14, "bold"),
            bg="#00e5ff",
            fg="black",
            padx=25,
            pady=12,
            command=self.start_test
        )
        self.start_button.pack(pady=25)

        # Status
        self.status_label = tk.Label(
            self.root,
            text="Ready",
            font=("Arial", 13, "bold"),
            fg="#00ff88",
            bg="#101820"
        )
        self.status_label.pack(pady=5)

        # Progress
        self.progress = ttk.Progressbar(
            self.root,
            length=550,
            mode="determinate"
        )
        self.progress.pack(pady=15)

        # Results frame
        results = tk.Frame(
            self.root,
            bg="#18232c"
        )
        results.pack(
            padx=40,
            pady=20,
            fill="both",
            expand=True
        )

        self.ping_value = self.create_result(
            results,
            "PING",
            "0 ms",
            0,
            0
        )

        self.download_value = self.create_result(
            results,
            "DOWNLOAD",
            "0 Mbps",
            0,
            1
        )

        self.upload_value = self.create_result(
            results,
            "UPLOAD",
            "0 Mbps",
            1,
            0
        )

        self.ip_value = self.create_result(
            results,
            "PUBLIC IP",
            "Unknown",
            1,
            1
        )

    def create_result(
        self,
        parent,
        title,
        value,
        row,
        column
    ):

        frame = tk.Frame(
            parent,
            bg="#18232c",
            width=300,
            height=130
        )

        frame.grid(
            row=row,
            column=column,
            padx=20,
            pady=20,
            sticky="nsew"
        )

        parent.grid_columnconfigure(
            column,
            weight=1
        )

        parent.grid_rowconfigure(
            row,
            weight=1
        )

        title_label = tk.Label(
            frame,
            text=title,
            font=("Arial", 13, "bold"),
            fg="#aaaaaa",
            bg="#18232c"
        )
        title_label.pack(pady=(20, 5))

        value_label = tk.Label(
            frame,
            text=value,
            font=("Arial", 22, "bold"),
            fg="#00e5ff",
            bg="#18232c"
        )
        value_label.pack()

        return value_label

    # ---------------------------------------------
    # START TEST
    # ---------------------------------------------

    def start_test(self):

        if self.testing:
            return

        self.testing = True

        self.start_button.config(
            state="disabled"
        )

        self.progress["value"] = 0

        thread = threading.Thread(
            target=self.run_test
        )

        thread.daemon = True
        thread.start()

    # ---------------------------------------------
    # RUN TEST
    # ---------------------------------------------

    def run_test(self):

        try:

            # Public IP
            self.update_status(
                "Finding public IP...",
                10
            )

            try:

                public_ip = urllib.request.urlopen(
                    "https://api.ipify.org",
                    timeout=10
                ).read().decode()

            except:

                public_ip = "Unavailable"

            self.root.after(
                0,
                lambda: self.ip_value.config(
                    text=public_ip
                )
            )

            # Ping
            self.update_status(
                "Testing latency...",
                25
            )

            ping = self.test_ping()

            self.root.after(
                0,
                lambda: self.ping_value.config(
                    text=f"{ping:.0f} ms"
                )
            )

            # Download
            self.update_status(
                "Testing download speed...",
                45
            )

            download = self.test_download()

            self.root.after(
                0,
                lambda: self.download_value.config(
                    text=f"{download:.2f} Mbps"
                )
            )

            # Upload
            self.update_status(
                "Testing upload speed...",
                75
            )

            upload = self.test_upload()

            self.root.after(
                0,
                lambda: self.upload_value.config(
                    text=f"{upload:.2f} Mbps"
                )
            )

            self.update_status(
                "Speed test completed!",
                100
            )

        except Exception as e:

            self.update_status(
                "Test failed: " + str(e),
                0
            )

        finally:

            self.testing = False

            self.root.after(
                0,
                lambda: self.start_button.config(
                    state="normal"
                )
            )

    # ---------------------------------------------
    # PING TEST
    # ---------------------------------------------

    def test_ping(self):

        hostname = "google.com"

        times = []

        for i in range(3):

            start = time.time()

            try:

                socket.gethostbyname(hostname)

                socket.create_connection(
                    (hostname, 80),
                    timeout=5
                ).close()

                end = time.time()

                times.append(
                    (end - start) * 1000
                )

            except:

                pass

        if times:
            return statistics.mean(times)

        return 0

    # ---------------------------------------------
    # DOWNLOAD TEST
    # ---------------------------------------------

    def test_download(self):

        # Public test file
        url = (
            "https://speedtest.wdc01.softlayer.com/"
            "downloads/test10.zip"
        )

        start_time = time.time()

        total_bytes = 0

        try:

            request = urllib.request.Request(
                url,
                headers={
                    "User-Agent": "Mozilla/5.0"
                }
            )

            response = urllib.request.urlopen(
                request,
                timeout=15
            )

            while True:

                data = response.read(
                    1024 * 1024
                )

                if not data:
                    break

                total_bytes += len(data)

                elapsed = (
                    time.time() - start_time
                )

                if elapsed >= 10:
                    break

            elapsed = time.time() - start_time

            if elapsed == 0:
                return 0

            bits = total_bytes * 8

            return bits / elapsed / 1_000_000

        except:

            return 0

    # ---------------------------------------------
    # UPLOAD TEST
    # ---------------------------------------------

    def test_upload(self):

        url = "https://httpbin.org/post"

        data = b"0" * (1024 * 1024)

        start_time = time.time()

        total_bytes = 0

        try:

            for i in range(3):

                request = urllib.request.Request(
                    url,
                    data=data,
                    method="POST",
                    headers={
                        "Content-Type":
                        "application/octet-stream"
                    }
                )

                urllib.request.urlopen(
                    request,
                    timeout=15
                ).read()

                total_bytes += len(data)

            elapsed = time.time() - start_time

            if elapsed == 0:
                return 0

            bits = total_bytes * 8

            return bits / elapsed / 1_000_000

        except:

            return 0

    # ---------------------------------------------
    # UPDATE GUI
    # ---------------------------------------------

    def update_status(
        self,
        message,
        progress
    ):

        self.root.after(
            0,
            lambda: self.status_label.config(
                text=message
            )
        )

        self.root.after(
            0,
            lambda: self.progress.config(
                value=progress
            )
        )


# ---------------------------------------------
# MAIN
# ---------------------------------------------

if __name__ == "__main__":

    root = tk.Tk()

    app = NetworkSpeedTester(root)

    root.mainloop()