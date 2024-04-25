from pulp import *
from datascan import MagazaVeritabani , UrunBulma

import time
import pickle

db = MagazaVeritabani(server='BTA22268\SQLEXPRESS', database='magazalar')

alici_veri_seti = db.alici_magaza_veriseti()
verici_veri_seti = db.verici_magaza_veriseti()
tasima_maliyetleri = db.tasima_maliyeti()
tasima_maliyetleri_dict = db.olustur_tasima_maliyetleri(tasima_maliyetleri)
verici_magaza_kodlari = db.verici_magaza_kodu()
alici_magaza_kodlari = db.alici_magaza_kodu()
urun_kodlari = db.urun_kodlari()
db.close()



ub = UrunBulma(alici_veri_seti, verici_veri_seti, tasima_maliyetleri_dict)

start_time = time.time()

transfer_oneri = {}

model = LpProblem("Magazalararasi_Transfer", LpMinimize)

x = LpVariable.dicts("miktar", [(i, j) for i in verici_magaza_kodlari for j in alici_magaza_kodlari], lowBound=0,
                     cat='Integer')

for urun in urun_kodlari:
    model_start_time = time.time()

    transfer_oneri[urun] = []

    model += lpSum(
        [ub.urun_tasima_maliyetleri(urun)[i][j] * x[(i, j)] for i in verici_magaza_kodlari for j in
         alici_magaza_kodlari]) \
             - lpSum(
        [ub.stok_maliyeti_arama(urun)[i] * x[(i, j)] for i in verici_magaza_kodlari for j in alici_magaza_kodlari]) \
             - lpSum(
        [ub.satis_kaybi_arama(urun)[j] * x[(i, j)] for i in verici_magaza_kodlari for j in alici_magaza_kodlari])

    model_end_time = time.time()
    model_duration = model_end_time - model_start_time

    solve_start_time = time.time()

    for j in alici_magaza_kodlari:
        model += lpSum([x[(i, j)] for i in verici_magaza_kodlari]) <= ub.urunu_alabilecek_magaza(urun)[j]

    for i in verici_magaza_kodlari:
        model += lpSum([x[(i, j)] for j in alici_magaza_kodlari]) <= ub.urunu_verebilecek_magaza(urun)[i]

    model.solve()

    solve_end_time = time.time()
    solve_duration = solve_end_time - solve_start_time

    for oneri in model.variables():
        if oneri.varValue > 0:
            transfer_oneri[urun].append(f"{urun}_" + oneri.name + " = " + str(oneri.varValue))

end_time = time.time()
calculation_time = end_time - start_time
urun_time = calculation_time / len(urun_kodlari)

print("Tek bir ürün için Model hesaplama süresi:", model_duration, "saniye")
print("Tek bir ürün için  Model Çözüm süresi", solve_duration, "saniye")
print("Toplam hesaplama süresi:", (calculation_time / 60), "dakika")
print("Urun basına ortalama hesap süresi:,", urun_time, "saniye")

with open ("data/transfer_oneri.pkl", "wb") as f:
    pickle.dump(transfer_oneri, f)