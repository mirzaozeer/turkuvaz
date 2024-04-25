import pyodbc
from collections import defaultdict

class MagazaVeritabani:
    def __init__(self, server, database):
        self.connection_string = f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;'
        self.conn = pyodbc.connect(self.connection_string)
        self.cursor = self.conn.cursor()

    def fetch_all(self, sql_query):
        self.cursor.execute(sql_query)
        return self.cursor.fetchall()

    def alici_magaza_veriseti(self):
        sql_query = '''
        SELECT alici_magaza_kodu, urun_kodu, adet, satis_kaybi_maliyeti
        FROM alici_magazalar
        ORDER BY alici_magaza_kodu, urun_kodu;'''
        data = self.fetch_all(sql_query)
        results = defaultdict(list)
        for row in data:
            alici_magaza_kodu = row[0]
            urun_detay = (row[1], row[2], row[3])
            results[alici_magaza_kodu].append(urun_detay)
        return [(k, v) for k, v in results.items()]

    def verici_magaza_veriseti(self):
        sql_query = '''
        SELECT verici_magaza_kodu, urun_kodu, adet, stok_maliyeti
        FROM verici_magazalar
        ORDER BY verici_magaza_kodu, urun_kodu;'''
        data = self.fetch_all(sql_query)
        results = defaultdict(list)
        for row in data:
            verici_magaza_kodu = row[0]
            urun_detay = (row[1], row[2], row[3])
            results[verici_magaza_kodu].append(urun_detay)
        return [(k, v) for k, v in results.items()]

    def tasima_maliyeti(self):
        sql_query = '''
        SELECT verici_magaza_kodu, alici_magaza_kodu, urun_kodu, AVG(tasima_maliyeti) as ortalama_tasima_maliyeti
        FROM tasima_maliyetleri
        GROUP BY verici_magaza_kodu, alici_magaza_kodu, urun_kodu
        ORDER BY verici_magaza_kodu, alici_magaza_kodu, urun_kodu;'''
        return [(row[0], row[1], row[2], row[3]) for row in self.fetch_all(sql_query)]

    def unique_codes(self, table, column):
        query = f"SELECT DISTINCT {column} FROM {table}"
        return [row[0] for row in self.fetch_all(query)]

    def verici_magaza_kodu(self):
        return self.unique_codes('verici_magazalar', 'verici_magaza_kodu')

    def alici_magaza_kodu(self):
        return self.unique_codes('alici_magazalar', 'alici_magaza_kodu')

    def urun_kodlari(self):
        return self.unique_codes('verici_magazalar', 'urun_kodu')

    def olustur_tasima_maliyetleri(self, veri_seti):
        maliyet_matrisi = {}
        for veri in veri_seti:
            verici_magaza, alici_magaza, urun_kodu, tasima_maliyeti = veri
            if urun_kodu not in maliyet_matrisi:
                maliyet_matrisi[urun_kodu] = {}
            if verici_magaza not in maliyet_matrisi[urun_kodu]:
                maliyet_matrisi[urun_kodu][verici_magaza] = {}
            maliyet_matrisi[urun_kodu][verici_magaza][alici_magaza] = tasima_maliyeti
        return maliyet_matrisi

    def close(self):
        self.conn.close()


class UrunBulma:
    def __init__(self, alici_veri_seti, verici_veri_seti, maliyet_matrisi):
        self.alici_veri_seti = alici_veri_seti
        self.verici_veri_seti = verici_veri_seti
        self.maliyet_matrisi = maliyet_matrisi

    def urunu_alabilecek_magaza(self, urun_kodu):
        alabilecek_magaza = []
        for magaza in self.alici_veri_seti:
            for urun in magaza[1]:
                if urun[0] == urun_kodu and urun[1] >= 0:
                    alabilecek_magaza.append((magaza[0], urun[1]))
        return dict(alabilecek_magaza)

    def urunu_verebilecek_magaza(self, urun_kodu):
        stok_verebilecek_magazalar = []
        for magaza in self.verici_veri_seti:
            for urun in magaza[1]:
                if urun[0] == urun_kodu and urun[1] >= 0:
                    stok_verebilecek_magazalar.append((magaza[0], urun[1]))
        return dict(stok_verebilecek_magazalar)

    def stok_maliyeti_arama(self, urun_kodu):
        stok_maliyetleri = []
        for magaza in self.verici_veri_seti:
            for urun in magaza[1]:
                if urun[0] == urun_kodu:
                    stok_maliyetleri.append((magaza[0], urun[2]))
        return dict(stok_maliyetleri)

    def satis_kaybi_arama(self, urun_kodu):
        satis_kaybi_maliyetleri = []
        for magaza in self.alici_veri_seti:
            for urun in magaza[1]:
                if urun[0] == urun_kodu:
                    satis_kaybi_maliyetleri.append((magaza[0], urun[2]))
        return dict(satis_kaybi_maliyetleri)

    def urun_tasima_maliyetleri(self, urun_kodu):
        if urun_kodu in self.maliyet_matrisi:
            return self.maliyet_matrisi[urun_kodu]
        else:
            return {}
