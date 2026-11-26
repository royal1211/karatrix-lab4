# Lab 4 - Task 2
# Open Addressing Hash Table
# Firewall Blacklist System


ACTIVE  = "ACTIVE"
EMPTY   = "EMPTY"
DELETED = "DELETED"

LINEAR    = "LINEAR"
QUADRATIC = "QUADRATIC"


# Cədvəlin bir xanası. Hər xana ya boş, ya silinmiş,
# ya da aktiv IP saxlayır.
class HashEntry:
    def __init__(self):
        self.ip = None
        self.status = EMPTY


class OpenAddressingHash:
    def __init__(self, size, mode=QUADRATIC):
        # Ölçünü dərhal sadə ədədə çeviririk,
        # çünki probing dövrünün tam olması üçün bu vacibdir.
        self.size = self.nextPrime(size)
        self.currentSize = 0
        self.mode = mode
        self.table = [HashEntry() for _ in range(self.size)]

    # ------------------------------------------------------------
    # Köməkçi funksiyalar
    # ------------------------------------------------------------
    def isPrime(self, n):
        if n < 2:
            return False
        i = 2
        while i * i <= n:
            if n % i == 0:
                return False
            i += 1
        return True

    def nextPrime(self, n):
        while not self.isPrime(n):
            n += 1
        return n

    # IP-lər üçün polynomial hash (a = 37).
    # IP-ni rəqəm kimi deyil, simvol-simvol hesablayırıq.
    def hashFunction(self, ip):
        value = 0
        for ch in ip:
            value = (value * 37 + ord(ch)) % self.size
        return value

    # Növbəti indeksi O(1) vaxtda tapırıq.
    # Quadratic üçün: H(i) = (H(i-1) + 2i - 1) mod N
    def nextStep(self, current_index, step):
        if self.mode == LINEAR:
            return (current_index + 1) % self.size
        return (current_index + 2 * step - 1) % self.size

    # ------------------------------------------------------------
    # Axtarış və yer tapma
    # ------------------------------------------------------------
    def findPos(self, ip):
        index = self.hashFunction(ip)
        firstDeleted = -1   # ilk rast gəlinən DELETED xananı yadda saxlayırıq

        for step in range(1, self.size + 1):
            entry = self.table[index]

            if entry.status == ACTIVE:
                if entry.ip == ip:
                    return index
            elif entry.status == DELETED:
                if firstDeleted == -1:
                    firstDeleted = index
            else:  # EMPTY
                # Yol boyu DELETED görmüşüksə, onu təkrar istifadə edirik.
                if firstDeleted != -1:
                    return firstDeleted
                return index

            index = self.nextStep(index, step)

        # Bütün cədvəli gəzdiksə və yalnız DELETED-lər varsa:
        return firstDeleted

    def loadFactor(self):
        return self.currentSize / self.size

    # ------------------------------------------------------------
    # Insert / Remove / Contains
    # ------------------------------------------------------------
    def insert(self, ip):
        # Əvvəlcə yoxlayırıq – təkrar əlavə etməyək.
        already, _ = self.contains(ip)
        if already:
            return False

        # Yük faktoru 0.5-i keçəcəksə, cədvəli böyüdürük.
        if (self.currentSize + 1) / self.size > 0.5:
            self.rehash()

        pos = self.findPos(ip)
        if pos == -1:
            return False

        self.table[pos].ip = ip
        self.table[pos].status = ACTIVE
        self.currentSize += 1
        return True

    # Lazy deletion – fiziki silmə yoxdur, sadəcə DELETED işarəsi qoyuruq.
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

    # ------------------------------------------------------------
    # Rehash
    # ------------------------------------------------------------
    # Rehash zamanı contains/insert çağırmırıq ki,
    # öz-özünə rekursiya baş verməsin.
    def insertWithoutResize(self, ip):
        pos = self.findPos(ip)
        if pos == -1:
            return False
        self.table[pos].ip = ip
        self.table[pos].status = ACTIVE
        self.currentSize += 1
        return True

    # Cədvəli 2x böyüdürük və DELETED-lər təbii şəkildə yox olur.
    def rehash(self):
        oldTable = self.table
        oldSize  = self.size

        self.size = self.nextPrime(2 * oldSize + 1)
        self.table = [HashEntry() for _ in range(self.size)]
        self.currentSize = 0

        for entry in oldTable:
            if entry.status == ACTIVE:
                self.insertWithoutResize(entry.ip)

    # ------------------------------------------------------------
    # Çap
    # ------------------------------------------------------------
    def display(self):
        print("\n========== HASH TABLE ==========")
        for i, entry in enumerate(self.table):
            value = entry.ip if entry.ip else ""
            print(f"{i} : {entry.status} {value}")
        print("--------------------------------")
        print("Aktiv elementlər :", self.currentSize)
        print("Cədvəlin ölçüsü :", self.size)
        print("Load Factor      :", round(self.loadFactor(), 2))
        print("================================")


# ==================================
# Test hissəsi
# ==================================
if __name__ == "__main__":

    # --- 1) LINEAR PROBING ---
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

    # --- 2) QUADRATIC PROBING ---
    print("\n===== QUADRATIC PROBING TEST =====")
    quadTable = OpenAddressingHash(11, QUADRATIC)

    for ip in ["10.0.0.1", "10.0.0.2", "10.0.0.3"]:
        if quadTable.insert(ip):
            print(ip, "əlavə edildi.")

    quadTable.display()

    found, probes = quadTable.contains("10.0.0.2")
    print("IP tapıldı:", found, "| Probe sayı:", probes)

    if quadTable.remove("10.0.0.2"):
        print("10.0.0.2 silindi (DELETED).")

    quadTable.display()

    # --- 3) DELETED xananın təkrar istifadəsi ---
    print("\n===== DELETED REUSE TEST =====")
    reuseTable = OpenAddressingHash(11, QUADRATIC)

    # Eyni indeksə düşən iki IP tapaq.
    groups = {}
    ip1 = ip2 = None
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

    # Eyni indeksə düşən yeni IP tapıb, DELETED yerinə yazırıq.
    ip3 = None
    for i in range(100, 200):
        candidate = f"192.168.1.{i}"
        if reuseTable.hashFunction(candidate) == reuseTable.hashFunction(ip1):
            ip3 = candidate
            break

    reuseTable.insert(ip3)
    print("Yeni IP (DELETED yerinə yazıldı):", ip3)
    reuseTable.display()

    # --- 4) REHASH ---
    print("\n===== REHASH TEST =====")
    testTable = OpenAddressingHash(5, QUADRATIC)
    print("Başlanğıc ölçü:", testTable.size)

    for ip in ["172.16.0.1", "172.16.0.2", "172.16.0.3"]:
        testTable.insert(ip)
        print(ip, "əlavə edildi | Cari ölçü:", testTable.size)

    testTable.display()
