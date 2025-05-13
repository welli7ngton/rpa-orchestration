import datetime
import time
import os


if __name__ == '__main__':
    print("\nIniciando script python")
    os.makedirs('./logs', exist_ok=True)

    time.sleep(5)

    data = datetime.datetime.now()
    filename = data.strftime("./logs/%Y-%m-%d_%H-%M-%S.log")

    with open(filename, "w") as f:
        f.write(str(data))

    print("\nFinalizando script python")
