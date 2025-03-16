from datetime import datetime, timedelta


def main():
    print((datetime.now() + timedelta(hours=2)).isoformat())


if __name__ == "__main__":
    main()

