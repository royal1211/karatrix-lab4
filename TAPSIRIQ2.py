
# Laboratory Work 4 - Task 2
# Open Addressing Hash Table
# Firewall Blacklist System

ACTIVE = "ACTIVE"
EMPTY = "EMPTY"
DELETED = "DELETED"

LINEAR = "LINEAR"
QUADRATIC = "QUADRATIC"


# Hash cedvelinin xanalari
class HashEntry:
    def __init__(self):
        self.ip = None
        self.status = EMPTY


class OpenAddressingHash:

    def __init__(self, size, mode):
        self.size = self.nextPrime(size)
        self.currentSize = 0
        self.mode = mode

        self.table = [
            HashEntry() for _ in range(self.size)
        ]

    # Sadə ədəd yoxlanışı
    def isPrime(self, n):
        if n < 2:
            return False

        for i in range(2, int(n ** 0.5) + 1):
            if n % i == 0:
                return False

        return True

    # Növbəti sadə ədəd
    def nextPrime(self, n):
        while not self.isPrime(n):
            n += 1

        return n

    # IP ünvanı üçün hash funksiyası
    def hashFunction(self, ip):
        value = 0

        for char in ip:
            value = (value * 37 + ord(char)) % self.size

        return value

    # Probing indeksinin hesablanması
    def getIndex(self, start, i):

        if self.mode == LINEAR:
            return (start + i) % self.size

        # Quadratic Probing
        # H(i) = (H(i-1) + 2i - 1) mod N

        index = start

        for step in range(1, i + 1):
            index = (
                index + 2 * step - 1
            ) % self.size

        return index

    # Elementin yerini tapmaq
    def findPos(self, ip):

        start = self.hashFunction(ip)
        firstDeleted = -1

        for i in range(self.size):

            index = self.getIndex(start, i)
            entry = self.table[index]

            if entry.status == ACTIVE:

                if entry.ip == ip:
                    return index

            elif entry.status == DELETED:

                if firstDeleted == -1:
                    firstDeleted = index

            elif entry.status == EMPTY:

                if firstDeleted != -1:
                    return firstDeleted

                return index

        return firstDeleted

    # Yük faktoru
    def loadFactor(self):
        return self.currentSize / self.size

    # Element əlavə etmək
    def insert(self, ip):

        # Əvvəlcə IP-nin artıq olub-olmadığını yoxlayırıq
        found, probes = self.contains(ip)

        if found:
            print(ip, "artıq mövcuddur!")
            return False

        # Yük faktoru 0.5-i keçəcəksə böyüdürük
        if (self.currentSize + 1) / self.size > 0.5:
            self.rehash()

        position = self.findPos(ip)

        if position == -1:
            return False

        self.table[position].ip = ip
        self.table[position].status = ACTIVE

        self.currentSize += 1

        print(ip, "əlavə edildi.")

        return True

    # IP ünvanını silmək
    def remove(self, ip):

        start = self.hashFunction(ip)

        for i in range(self.size):

            index = self.getIndex(start, i)
            entry = self.table[index]

            if entry.status == EMPTY:
                return False

            if entry.status == ACTIVE and entry.ip == ip:

                # Lazy Deletion
                entry.status = DELETED

                self.currentSize -= 1

                print(ip, "silindi (DELETED).")

                return True

        print(ip, "tapılmadı.")
        return False

    # IP ünvanını axtarmaq
    def contains(self, ip):

        start = self.hashFunction(ip)
        probes = 0

        for i in range(self.size):

            index = self.getIndex(start, i)
            entry = self.table[index]

            probes += 1

            if entry.status == EMPTY:
                return False, probes

            if entry.status == ACTIVE and entry.ip == ip:
                return True, probes

        return False, probes

    # Rehash zamanı element əlavə etmək
    # Bu metod yenidən rehash çağırmır
    def insertWithoutResize(self, ip):

        position = self.findPos(ip)

        if position == -1:
            return False

        self.table[position].ip = ip
        self.table[position].status = ACTIVE

        self.currentSize += 1

        return True

    # Hash cədvəlini böyütmək
    def rehash(self):

        oldTable = self.table
        oldSize = self.size

        self.size = self.nextPrime(2 * oldSize + 1)

        self.table = [
            HashEntry() for _ in range(self.size)
        ]

        self.currentSize = 0

        # Yalnız ACTIVE elementləri köçürürük
        for entry in oldTable:

            if entry.status == ACTIVE:
                self.insertWithoutResize(entry.ip)

        print(
            "Rehash tamamlandı!",
            "Köhnə ölçü:", oldSize,
            "Yeni ölçü:", self.size
        )

    # Hash cədvəlini göstərmək
    def display(self):

        print("\n========== HASH TABLE ==========")

        for i, entry in enumerate(self.table):

            print(
                i, ":",
                entry.status,
                entry.ip if entry.ip else ""
            )

        print("--------------------------------")
        print("Aktiv elementlər:", self.currentSize)
        print("Cədvəlin ölçüsü:", self.size)
        print("Load Factor:", round(self.loadFactor(), 2))
        print("================================")


# ==================================
# LINEAR PROBING TEST
# ==================================

print("\n===== LINEAR PROBING TEST =====")

linearTable = OpenAddressingHash(11, LINEAR)

linearTable.insert("192.168.1.10")
linearTable.insert("192.168.1.20")
linearTable.insert("192.168.1.30")

linearTable.display()

found, probes = linearTable.contains("192.168.1.20")

print("IP tapıldı:", found)
print("Probe sayı:", probes)

linearTable.remove("192.168.1.20")

linearTable.display()


# ==================================
# QUADRATIC PROBING TEST
# ==================================

print("\n===== QUADRATIC PROBING TEST =====")

quadraticTable = OpenAddressingHash(11, QUADRATIC)

quadraticTable.insert("10.0.0.1")
quadraticTable.insert("10.0.0.2")
quadraticTable.insert("10.0.0.3")

quadraticTable.display()

found, probes = quadraticTable.contains("10.0.0.2")

print("IP tapıldı:", found)
print("Probe sayı:", probes)

quadraticTable.remove("10.0.0.2")

quadraticTable.display()


# ==================================
# DELETED XANANIN YENIDEN ISTIFADESI
# ==================================

print("\n===== DELETED REUSE TEST =====")

reuseTable = OpenAddressingHash(11, LINEAR)

# Eyni indeksə düşən IP-ləri tapırıq
groups = {}

for i in range(100):

    ip = f"192.168.1.{i}"
    index = reuseTable.hashFunction(ip)

    if index in groups:
        ip1 = groups[index]
        ip2 = ip
        break

    groups[index] = ip

print("Birinci IP:", ip1)
print("Ikinci IP:", ip2)

reuseTable.insert(ip1)
reuseTable.insert(ip2)

reuseTable.display()

# Birinci IP-ni silirik
reuseTable.remove(ip1)

# Eyni hash indeksinə düşən üçüncü IP tapırıq
ip3 = None

for i in range(100, 200):

    candidate = f"192.168.1.{i}"

    if reuseTable.hashFunction(candidate) == reuseTable.hashFunction(ip1):
        ip3 = candidate
        break

# DELETED xana yenidən istifadə olunur
reuseTable.insert(ip3)

print("Yeni IP:", ip3)

reuseTable.display()


# ==================================
# REHASH TEST
# ==================================

print("\n===== REHASH TEST =====")

testTable = OpenAddressingHash(5, LINEAR)

testTable.insert("172.16.0.1")
testTable.insert("172.16.0.2")
testTable.insert("172.16.0.3")

testTable.display()

print("\n===== PROGRAM FINISHED =====")
