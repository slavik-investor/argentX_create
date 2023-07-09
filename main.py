from worker import Worker

EXT_ID = "cjmkdbmbpnchheocmjjpdjmeinpghhig"
PASSWORD = "$0meHardPa$$w0rd"
SEEDS_PATH = "seeds.txt"
IDS_PATH = "ids.txt"


def main():
    worker = Worker(IDS_PATH, SEEDS_PATH, PASSWORD, EXT_ID)
    worker.run_work()


if __name__ == "__main__":
    main()
