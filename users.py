import psutil

def online():
    for u in psutil.users():
        print(u)


if __name__ == '__main__':
    online()