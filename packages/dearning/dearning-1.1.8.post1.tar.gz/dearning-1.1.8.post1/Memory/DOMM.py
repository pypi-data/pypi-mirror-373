import os
import shelve
from tinydb import TinyDB, Query
import multiprocessing
import json

class DOMM:
    def __init__(self, mem_name="DATAI", dir_path="dearning/memory"):
        self.dir_path = dir_path
        self.base_name = mem_name

        os.makedirs(self.dir_path, exist_ok=True)

        # Path file
        self.shelve_file = os.path.join(self.dir_path, self.base_name + ".db")
        self.json_file = os.path.join(self.dir_path, self.base_name + ".json")
        self.script_file = os.path.join(self.dir_path, self.base_name + ".py")

        # Inisialisasi database
        self.shelf = shelve.open(self.shelve_file)
        self.tiny = TinyDB(self.json_file)

        # Buat DATAI.py jika belum ada
        if not os.path.exists(self.script_file):
            with open(self.script_file, "w") as f:
                f.write("# File memory AI: {}\nDATA = {}".format(self.base_name, {}))

    # === Cek ukuran file (max 10MB)
    def check_size(self):
        total = 0
        for file in [self.shelve_file + ".db", self.json_file, self.script_file]:
            if os.path.exists(file):
                total += os.path.getsize(file)
        return total <= 10 * 1024 * 1024  # <= 10MB

    # === Fungsi untuk menyimpan model ke shelve
    def save_model(self, key, data):
        if not self.check_size():
            raise Exception("Ukuran file memory melebihi 10MB.")
        self.shelf[key] = data
        self.shelf.sync()

    def load_model(self, key):
        return self.shelf.get(key, None)

    def delete_model(self, key):
        if key in self.shelf:
            del self.shelf[key]

    def clear_model(self):
        self.shelf.clear()

    # === Fungsi untuk TinyDB
    def add_experience(self, state, action, reward):
        if not self.check_size():
            raise Exception("Ukuran file memory melebihi 10MB.")
        self.tiny.insert({
            "state": state,
            "action": action,
            "reward": reward
        })

    def search_experience(self, min_reward=0.0):
        Q = Query()
        return self.tiny.search(Q.reward >= min_reward)

    def clear_experience(self):
        self.tiny.truncate()

    # === Fungsi untuk menyimpan data manual ke DATAI.py
    def dump_to_script(self):
        with open(self.script_file, "w") as f:
            combined_data = {
                "shelve": dict(self.shelf),
                "experience": self.tiny.all()
            }
            f.write("# Memory export file\n")
            f.write("DATA = ")
            json.dump(combined_data, f, indent=4)

    # === Fungsi untuk membuat file baru dengan nama custom
    def add_memory_file(self, name):
        new_path = os.path.join(self.dir_path, name + ".py")
        if os.path.exists(new_path):
            return "File sudah ada!"
        with open(new_path, "w") as f:
            f.write("# File memory tambahan\nDATA = {}")
        return "File memory baru berhasil dibuat: " + name + ".py"

    # === Tutup database
    def close(self):
        self.shelf.close()
        self.tiny.close()