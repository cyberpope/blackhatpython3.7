import queue, threading, os, requests

threads = 10

target = 'http://www.blackhatpython.com'
directory = './something'
filters = ['.jpg', '.gif', '.png', '.css']

os.chdir(directory)

web_paths = queue.Queue()

for r, d, f in os.walk('.'):
    for files in f:
        remote_path = '%s/%s' % (r, files)
        if remote_path.startswith('.'):
            remote_path = remote_path[1:]
        if os.path.splitext(files)[1] not in filters:
            web_paths.put(remote_path)


def test_remote():
    while not web_paths.empty():
        path = web_paths.get()
        url = '%s%s' % (target, path)

        response = requests.request(url)

        if response.status_code == 200:
            print('[%d] => %s' % (response.status_code, path))
            response.close()

        if response.status_code == 403:
            print('Failed: %s' % response.status_code)
            pass


for i in range(threads):
    print('Spawning thread: %d' % i)
    t = threading.Thread(target=test_remote)
    t.start()

