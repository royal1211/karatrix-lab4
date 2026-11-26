# ============================================
# University Library Catalog System
# Separate Chaining + MAD Compression
# ============================================


# ---------- Book ----------
class Book:
    def __init__(self, isbn, title, author, isAvailable=True):
        self.isbn = isbn
        self.title = title
        self.author = author
        self.isAvailable = isAvailable

    def __str__(self):
        status = "Available" if self.isAvailable else "Borrowed"
        return (f"ISBN: {self.isbn} | Title: {self.title} | "
                f"Author: {self.author} | Status: {status}")


# ---------- Hash function ----------
# Horner's rule ilə polynomial hash (a = 37).
# ISBN-ı əvvəlcə təmizləyirik – tire və boşluqlar yığışdırılır.
def polynomial_hash(isbn):
    h = 0
    a = 37
    isbn = isbn.replace("-", "").replace(" ", "").upper()
    for ch in isbn:
        h = h * a + ord(ch)
    return h


# ---------- Compression ----------
def division_method(h, N):
    return h % N


def is_prime(n):
    if n < 2:
        return False
    i = 2
    while i * i <= n:
        if n % i == 0:
            return False
        i += 1
    return True


def next_prime(n):
    while not is_prime(n):
        n += 1
    return n


# MAD = Multiply-Add-Divide
def mad_method(h, N):
    p = next_prime(N + 1)
    a = 37 % (p - 1) + 1
    b = 17 % p
    return ((a * h + b) % p) % N


# ---------- Node & LinkedList ----------
class Node:
    def __init__(self, book):
        self.book = book
        self.next = None


class LinkedList:
    def __init__(self):
        self.head = None

    def insert(self, book):
        node = Node(book)
        if self.head is None:
            self.head = node
            return
        cur = self.head
        while cur.next:
            cur = cur.next
        cur.next = node

    def search(self, isbn):
        cur = self.head
        while cur:
            if cur.book.isbn == isbn:
                return cur.book
            cur = cur.next
        return None

    def delete(self, isbn):
        cur = self.head
        prev = None
        while cur:
            if cur.book.isbn == isbn:
                if prev is None:
                    self.head = cur.next
                else:
                    prev.next = cur.next
                return True
            prev = cur
            cur = cur.next
        return False


# ---------- HashTable ----------
class HashTable:
    def __init__(self, capacity=5, method="MAD"):
        self.capacity = capacity
        self.min_capacity = capacity     # shrink üçün alt sərhəd
        self.size = 0
        self.method = method.upper()
        self.table = [LinkedList() for _ in range(capacity)]

    def get_index(self, isbn):
        h = polynomial_hash(isbn)
        if self.method == "DIVISION":
            return division_method(h, self.capacity)
        return mad_method(h, self.capacity)

    def load_factor(self):
        return self.size / self.capacity

    def put(self, book):
        idx = self.get_index(book.isbn)

        # Eyni ISBN varsa – sadəcə məlumatı yeniləyirik.
        existing = self.table[idx].search(book.isbn)
        if existing is not None:
            print("Book already exists. Updating information.")
            existing.title = book.title
            existing.author = book.author
            existing.isAvailable = book.isAvailable
            return

        self.table[idx].insert(book)
        self.size += 1

        # Load factor 1-i keçsə, cədvəli iki qat böyüdürük.
        if self.load_factor() > 1.0:
            self.resize(self.capacity * 2)

        print("Book added successfully!")

    def get(self, isbn):
        idx = self.get_index(isbn)
        return self.table[idx].search(isbn)

    def remove(self, isbn):
        idx = self.get_index(isbn)
        if not self.table[idx].delete(isbn):
            print("Book not found!")
            return False

        self.size -= 1
        print("Book deleted successfully!")

        # Cədvəl çox boşalsa – kiçildirik, amma min ölçüdən aşağı düşmürük.
        if self.load_factor() < 0.25 and self.capacity > self.min_capacity:
            new_cap = max(self.min_capacity, self.capacity // 2)
            self.resize(new_cap)

        return True

    def resize(self, new_capacity):
        print("\nResizing Hash Table...")
        print(f"Old Capacity: {self.capacity}")

        old_table = self.table
        self.capacity = new_capacity
        self.table = [LinkedList() for _ in range(new_capacity)]

        # Bütün mövcud kitabları yeni ölçüyə uyğun yenidən yerləşdiririk.
        for lst in old_table:
            cur = lst.head
            while cur:
                book = cur.book
                self.table[self.get_index(book.isbn)].insert(book)
                cur = cur.next

        print(f"New Capacity: {self.capacity}")
        print("Rehash completed!\n")

    def display_all(self):
        print("\n========== ALL BOOKS ==========")
        if self.size == 0:
            print("Library is empty!")
            return
        for lst in self.table:
            cur = lst.head
            while cur:
                print(cur.book)
                cur = cur.next

    def display_table(self):
        print("\n========== HASH TABLE ==========")
        for i, lst in enumerate(self.table):
            print(f"Index {i}:", end=" ")
            cur = lst.head
            if cur is None:
                print("None")
                continue
            while cur:
                print(f"[{cur.book.isbn}]", end=" -> ")
                cur = cur.next
            print("None")

    def statistics(self):
        print("\n========== STATISTICS ==========")
        print("Total Books:", self.size)
        print("Capacity:", self.capacity)
        print("Load Factor:", round(self.load_factor(), 3))
        print("Compression Method:", self.method)


# ---------- Main ----------
def main():
    print("===================================")
    print(" UNIVERSITY LIBRARY CATALOG")
    print("===================================")

    print("\nChoose Compression Method:")
    print("1. Division Method")
    print("2. MAD Method")
    choice = input("Enter choice: ").strip()
    method = "DIVISION" if choice == "1" else "MAD"

    library = HashTable(capacity=5, method=method)

    while True:
        print("\n========== MAIN MENU ==========")
        print("1. Add Book")
        print("2. Search Book")
        print("3. Delete Book")
        print("4. Display All Books")
        print("5. Display Hash Table")
        print("6. Show Statistics")
        print("7. Exit")

        option = input("\nChoose an option: ").strip()

        if option == "1":
            isbn = input("Enter ISBN: ").strip()
            title = input("Enter Title: ").strip()
            author = input("Enter Author: ").strip()
            library.put(Book(isbn, title, author, True))

        elif option == "2":
            isbn = input("Enter ISBN to search: ").strip()
            book = library.get(isbn)
            if book:
                print("\nBook Found!")
                print(book)
            else:
                print("Book not found!")

        elif option == "3":
            isbn = input("Enter ISBN to delete: ").strip()
            library.remove(isbn)

        elif option == "4":
            library.display_all()

        elif option == "5":
            library.display_table()

        elif option == "6":
            library.statistics()

        elif option == "7":
            print("\nThank you for using the Library System!")
            break

        else:
            print("Invalid option! Try again.")


if __name__ == "__main__":
    main()
