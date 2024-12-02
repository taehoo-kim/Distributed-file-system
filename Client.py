# client.py 파일 내용
import requests
import os
import hashlib
import bisect

class ConsistentHashing:
    def __init__(self, replicas=3):
        self.replicas = replicas
        self.ring = dict()
        self.sorted_keys = []

    def _hash(self, key):
        return int(hashlib.md5(key.encode('utf-8')).hexdigest(), 16)

    def add_node(self, node):
        for i in range(self.replicas):
            hashed_key = self._hash(f"{node}-{i}")
            self.ring[hashed_key] = node
            bisect.insort(self.sorted_keys, hashed_key)

    def remove_node(self, node):
        for i in range(self.replicas):
            hashed_key = self._hash(f"{node}-{i}")
            self.ring.pop(hashed_key)
            self.sorted_keys.remove(hashed_key)

    def get_node(self, key):
        if not self.ring:
            return None
        hashed_key = self._hash(key)
        idx = bisect.bisect(self.sorted_keys, hashed_key)
        if idx == len(self.sorted_keys):
            idx = 0
        return self.ring[self.sorted_keys[idx]]

# 서버 목록과 Consistent Hashing 인스턴스 초기화
servers = ['http://localhost:5000']
ch = ConsistentHashing()

for server in servers:
    ch.add_node(server)

def upload_file(filepath):
    filename = os.path.basename(filepath)
    server = ch.get_node(filename)
    url = f"{server}/upload"
    with open(filepath, 'rb') as f:
        files = {'file': f}
        response = requests.post(url, files=files)
        print(response.json())

def download_file(filename, dest_path):
    server = ch.get_node(filename)
    url = f"{server}/download/{filename}"
    response = requests.get(url)
    with open(dest_path, 'wb') as f:
        f.write(response.content)
    print(f'File {filename} downloaded to {dest_path}')

if __name__ == '__main__':
    # Example usage:
    upload_file('test.txt')
    download_file('test.txt', 'downloaded_test.txt')
