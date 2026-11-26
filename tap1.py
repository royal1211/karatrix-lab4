# ============================================

# UNIVERSITY LIBRARY CATALOG SYSTEM

# Separate Chaining + MAD Compression

# ============================================


# 1. BOOK CLASS

# ============================================


class Book:

  def __init__(self, isbn, title, author, isAvailable=True):

    self.isbn = isbn

    self.title = title

    self.author = author

    self.isAvailable = isAvailable


  def __str__(self):

    status = "Available" if self.isAvailable else "Borrowed"


    return (

      f"ISBN: {self.isbn} | "

      f"Title: {self.title} | "

      f"Author: {self.author} | "

      f"Status: {status}"

    )



# 2. POLYNOMIAL HASH FUNCTION

# Horner's Rule, a = 37

# ============================================


def polynomial_hash(isbn):

  h = 0

  a = 37


  # Remove spaces and hyphens

  isbn = isbn.replace("-", "").replace(" ", "").upper()


  for char in isbn:

    h = h * a + ord(char)


  return h



# 3. COMPRESSION METHODS

# ============================================


# Division Method

def division_method(hash_value, N):

  return hash_value % N



# Find next prime number

def is_prime(n):

  if n < 2:

    return False


  for i in range(2, int(n ** 0.5) + 1):

    if n % i == 0:

      return False


  return True



def next_prime(n):

  while not is_prime(n):

    n += 1


  return n



# MAD Compression Method

def mad_method(hash_value, N):

  p = next_prime(N + 1)


  a = 37 % (p - 1) + 1

  b = 17 % p


  return ((a * hash_value + b) % p) % N



# 4. NODE CLASS

# ============================================


class Node:

  def __init__(self, book):

    self.book = book

    self.next = None



# 5. LINKED LIST CLASS

# ============================================


class LinkedList:


  def __init__(self):

    self.head = None


  # Insert book

  def insert(self, book):

    new_node = Node(book)


    if self.head is None:

      self.head = new_node

      return


    current = self.head


    while current.next is not None:

      current = current.next


    current.next = new_node


  # Search book

  def search(self, isbn):

    current = self.head


    while current is not None:

      if current.book.isbn == isbn:

        return current.book


      current = current.next


    return None


  # Delete book

  def delete(self, isbn):

    current = self.head

    previous = None


    while current is not None:


      if current.book.isbn == isbn:


        if previous is None:

          self.head = current.next

        else:

          previous.next = current.next


        return True


      previous = current

      current = current.next


    return False



# 6. HASH TABLE CLASS

# ============================================


class HashTable:


  def __init__(self, capacity=5, method="MAD"):


    self.capacity = capacity

    self.min_capacity = capacity


    self.size = 0

    self.method = method.upper()


    self.table = [

      LinkedList() for _ in range(capacity)

    ]


  # Calculate hash index

  def get_index(self, isbn):


    hash_value = polynomial_hash(isbn)


    if self.method == "DIVISION":

      return division_method(

        hash_value, self.capacity

      )


    return mad_method(

      hash_value, self.capacity

    )


  # Load Factor

  def load_factor(self):

    return self.size / self.capacity


  # Insert book

  def put(self, book):


    index = self.get_index(book.isbn)


    # Check duplicate ISBN

    existing = self.table[index].search(book.isbn)


    if existing is not None:

      print("Book already exists. Updating information.")

      existing.title = book.title

      existing.author = book.author

      existing.isAvailable = book.isAvailable

      return


    self.table[index].insert(book)

    self.size += 1


    # Dynamic resizing

    if self.load_factor() > 1.0:

      self.resize(self.capacity * 2)


    print("Book added successfully!")


  # Search book

  def get(self, isbn):


    index = self.get_index(isbn)


    return self.table[index].search(isbn)


  # Delete book

  def remove(self, isbn):


    index = self.get_index(isbn)


    deleted = self.table[index].delete(isbn)


    if deleted:

      self.size -= 1

      print("Book deleted successfully!")


      # Shrink if load factor < 0.25

      if (

        self.load_factor() < 0.25

        and self.capacity > self.min_capacity

      ):

        new_capacity = max(

          self.min_capacity,

          self.capacity // 2

        )


        self.resize(new_capacity)


      return True


    print("Book not found!")

    return False


  # Resize and Rehash

  def resize(self, new_capacity):


    print("\nResizing Hash Table...")

    print(

      f"Old Capacity: {self.capacity}"

    )


    old_table = self.table


    self.capacity = new_capacity


    self.table = [

      LinkedList() for _ in range(new_capacity)

    ]


    # Rehash all books

    for linked_list in old_table:


      current = linked_list.head


      while current is not None:


        book = current.book


        new_index = self.get_index(book.isbn)


        self.table[new_index].insert(book)


        current = current.next


    print(

      f"New Capacity: {self.capacity}"

    )

    print("Rehash completed!\n")


  # Display all books

  def display_all(self):


    print("\n========== ALL BOOKS ==========")


    if self.size == 0:

      print("Library is empty!")

      return


    for linked_list in self.table:


      current = linked_list.head


      while current is not None:

        print(current.book)

        current = current.next


  # Display Hash Table

  def display_table(self):


    print("\n========== HASH TABLE ==========")


    for i, linked_list in enumerate(self.table):


      print(f"Index {i}:", end=" ")


      current = linked_list.head


      if current is None:

        print("None")

        continue


      while current is not None:


        print(

          f"[{current.book.isbn}]",

          end=" -> "

        )


        current = current.next


      print("None")


  # Display statistics

  def statistics(self):


    print("\n========== STATISTICS ==========")


    print("Total Books:", self.size)

    print("Capacity:", self.capacity)


    print(

      "Load Factor:",

      round(self.load_factor(), 3)

    )


    print("Compression Method:", self.method)



# 7. MAIN PROGRAM / USER INTERFACE

# ============================================


def main():


  print("===================================")

  print(" UNIVERSITY LIBRARY CATALOG")

  print("===================================")


  print("\nChoose Compression Method:")

  print("1. Division Method")

  print("2. MAD Method")


  choice = input("Enter choice: ").strip()


  method = "DIVISION" if choice == "1" else "MAD"


  library = HashTable(

    capacity=5,

    method=method

  )


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


    # ADD BOOK

    if option == "1":


      isbn = input("Enter ISBN: ").strip()

      title = input("Enter Title: ").strip()

      author = input("Enter Author: ").strip()


      book = Book(

        isbn,

        title,

        author,

        True

      )


      library.put(book)


    # SEARCH BOOK

    elif option == "2":


      isbn = input("Enter ISBN to search: ").strip()


      book = library.get(isbn)


      if book is not None:

        print("\nBook Found!")

        print(book)

      else:

        print("Book not found!")


    # DELETE BOOK

    elif option == "3":


      isbn = input("Enter ISBN to delete: ").strip()


      library.remove(isbn)


    # DISPLAY ALL

    elif option == "4":


      library.display_all()


    # DISPLAY HASH TABLE

    elif option == "5":


      library.display_table()


    # STATISTICS

    elif option == "6":


      library.statistics()


    # EXIT

    elif option == "7":


      print("\nThank you for using the Library System!")

      break


    else:

      print("Invalid option! Try again.")



# 8. PROGRAM ENTRY POINT

# ============================================


if __name__ == "__main__":

  main()
