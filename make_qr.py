"""Creates phone_qr.png: a QR code for opening StudyFlow AI from a phone on the same Wi-Fi."""
import socket
import sys

PORT = 8501


def lan_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("10.255.255.255", 1))  # no data is sent; just picks the Wi-Fi/LAN adapter
        return s.getsockname()[0]
    finally:
        s.close()


def main():
    try:
        import qrcode
    except ImportError:
        print("QR step skipped: package 'qrcode' is not installed.")
        return 0
    try:
        ip = lan_ip()
    except OSError:
        print("QR step skipped: could not detect your Wi-Fi address (are you connected?).")
        return 0
    url = f"http://{ip}:{PORT}"
    qrcode.make(url).save("phone_qr.png")
    print(f"\n  Phone link: {url}")
    print("  A QR code was saved as phone_qr.png - scan it with your phone camera.\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
