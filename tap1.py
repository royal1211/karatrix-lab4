# Laboratory Work 4 - Task 2
# Open Addressing Hash Table
# Firewall Blacklist System

ACTIVE = "ACTIVE"
EMPTY = "EMPTY"
DELETED = "DELETED"

LINEAR = "LINEAR"
QUADRATIC = "QUADRATIC"


# Hash cədvəlinin xanaları
class HashEntry:
    def __init__(self):
        self.ip = None
        self.status = EMPTY


class OpenAddressingHash:
    def __init__(self, size, mode=QUADRATIC):
        self.size = self.nextPrime(size)
        self.currentSize = 0
        self.mode = mode
        self.table = [HashEntry() for _ in range(self.size)]

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

    # IP ünvanı üçün polinom həş funksiyası (a = 37)
    def hashFunction(self, ip):
        value = 0
        for char in ip:
            value = (value * 37 + ord(char)) % self.size
        return value

    # Növbəti addım indeksinin O(1) vaxtda hesablanması
    # Quadratic Probing üçün: H(i) = (H(i-1) + 2i - 1) mod N
    def nextStep(self, current_index, step):
        if self.mode == LINEAR:
            return (current_index + 1) % self.size
        return (current_index + 2 * step - 1) % self.size

    # Elementin yerini tapmaq
    def findPos(self, ip):
        index = self.hashFunction(ip)
        firstDeleted = -1

        for step in range(1, self.size + 1):
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

            index = self.nextStep(index, step)

        return firstDeleted

    # Yük faktoru (Load Factor)
    def loadFactor(self):
        return self.currentSize / self.size

    # Element əlavə etmək
    def insert(self, ip):
        found, _ = self.contains(ip)
        if found:
            return False

        # Yük faktoru 0.5-i keçəcəksə cədvəli böyüdürük
        if (self.currentSize + 1) / self.size > 0.5:
            self.rehash()

        position = self.findPos(ip)
        if position == -1:
            return False

        self.table[position].ip = ip
        self.table[position].status = ACTIVE
        self.currentSize += 1
        return True

    # IP ünvanını silmək (Lazy Deletion)
    def remove(self, ip):
        index = self.hashFunction(ip)

        for step in range(1, self.size + 1):
            entry = self.table[index]

            if entry.status == EMPTY:
                return False

            if entry.status == ACTIVE and entry.ip == ip:
                entry.status = DELETED
                entry.ip = None
                self.currentSize -= 1
                return True

            index = self.nextStep(index, step)

        return False

    # IP ünvanını axtarmaq və probe sayını qaytarmaq
    def contains(self, ip):
        index = self.hashFunction(ip)
        probes = 0

        for step in range(1, self.size + 1):
            entry = self.table[index]
            probes += 1

            if entry.status == EMPTY:
                return False, probes

            if entry.status == ACTIVE and entry.ip == ip:
                return True, probes

            index = self.nextStep(index, step)

        return False, probes

    # Rehash zamanı element əlavə etmək (yenidən rehash çağırmır)
    def insertWithoutResize(self, ip):
        position = self.findPos(ip)
        if position == -1:
            return False

        self.table[position].ip = ip
        self.table[position].status = ACTIVE
        self.currentSize += 1
        return True

    # Hash cədvəlini böyütmək və DELETED elementləri təmizləmək
    def rehash(self):
        oldTable = self.table
        oldSize = self.size

        self.size = self.nextPrime(2 * oldSize + 1)
        self.table = [HashEntry() for _ in range(self.size)]
        self.currentSize = 0

        for entry in oldTable:
            if entry.status == ACTIVE:
                self.insertWithoutResize(entry.ip)

    # Hash cədvəlini konsolda göstərmək
    def display(self):
        print("\n========== HASH TABLE ==========")
        for i, entry in enumerate(self.table):
            print(f"{i} : {entry.status} {entry.ip if entry.ip else ''}")
        print("--------------------------------")
        print("Aktiv elementlər:", self.currentSize)
        print("Cədvəlin ölçüsü:", self.size)
        print("Load Factor:", round(self.loadFactor(), 2))
        print("================================")


# ==================================
# TEST BLOKU (Müdafiə və Yoxlama üçün)
# ==================================
if __name__ == "__main__":
    # 1. LINEAR PROBING TEST
    print("\n===== LINEAR PROBING TEST =====")
    linearTable = OpenAddressingHash(11, LINEAR)

    for ip in ["192.168.1.10", "192.168.1.20", "192.168.1.30"]:
        if linearTable.insert(ip):
            print(ip, "əlavə edildi.")

    linearTable.display()

    found, probes = linearTable.contains("192.168.1.20")
    print("IP tapıldı:", found, "| Probe sayı:", probes)

    if linearTable.remove("192.168.1.20"):
        print("192.168.1.20 silindi (DELETED).")

    linearTable.display()

    # 2. QUADRATIC PROBING TEST
    print("\n===== QUADRATIC PROBING TEST =====")
    quadraticTable = OpenAddressingHash(11, QUADRATIC)

    for ip in ["10.0.0.1", "10.0.0.2", "10.0.0.3"]:
        if quadraticTable.insert(ip):
            print(ip, "əlavə edildi.")

    quadraticTable.display()

    found, probes = quadraticTable.contains("10.0.0.2")
    print("IP tapıldı:", found, "| Probe sayı:", probes)

    if quadraticTable.remove("10.0.0.2"):
        print("10.0.0.2 silindi (DELETED).")

    quadraticTable.display()

    # 3. DELETED XANANIN YENİDƏN İSTİFADƏSİ
    print("\n===== DELETED REUSE TEST =====")
    reuseTable = OpenAddressingHash(11, QUADRATIC)

    groups = {}
    for i in range(100):
        ip = f"192.168.1.{i}"
        idx = reuseTable.hashFunction(ip)
        if idx in groups:
            ip1 = groups[idx]
            ip2 = ip
            break
        groups[idx] = ip

    print("Eyni indeksə düşən IP-lər:", ip1, "və", ip2)
    reuseTable.insert(ip1)
    reuseTable.insert(ip2)
    reuseTable.display()

    reuseTable.remove(ip1)
    print(ip1, "silindi (DELETED).")

    ip3 = None
    for i in range(100, 200):
        candidate = f"192.168.1.{i}"
        if reuseTable.hashFunction(candidate) == reuseTable.hashFunction(ip1):
            ip3 = candidate
            break

    reuseTable.insert(ip3)
    print("Yeni IP (DELETED yerinə yazıldı):", ip3)
    reuseTable.display()

    # 4. REHASH TEST
    print("\n===== REHASH TEST =====")
    testTable = OpenAddressingHash(5, QUADRATIC)
    print("Başlanğıc ölçü:", testTable.size)

    for ip in ["172.16.0.1", "172.16.0.2", "172.16.0.3"]:
        testTable.insert(ip)
        print(ip, "əlavə edildi | Cari ölçü:", testTable.size)

    testTable.display()
