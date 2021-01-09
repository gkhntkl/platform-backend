from django.contrib import admin
from django.urls import path,include,re_path

from django.db import transaction
import datetime


from slot.models import Slot
from city.models import City

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/hall/', include('hall.urls')),
    path('api/user/', include('user.urls')),
    path('api/slot/', include('slot.urls')),
    path('api/reservation/', include('reservation.urls')),
    ]



@transaction.atomic
def createDateTable():
    today = datetime.date.today()
    i = today
    count = 1
    while count != 1850:
        day = i
        slot = Slot.objects.filter(day=day)
        if not slot:
            Slot.objects.create(day=day)

        i = i + datetime.timedelta(days=1)
        count = count + 1

createDateTable()

cities = {
    "1": "ADANA",
    "2": "ADIYAMAN",
    "3": "AFYONKARAHİSAR",
    "4": "AĞRI",
    "5": "AMASYA",
    "6": "ANKARA",
    "7": "ANTALYA",
    "8": "ARTVİN",
    "9": "AYDIN",
    "10": "BALIKESİR",
    "11": "BİLECİK",
    "12": "BİNGÖL",
    "13": "BİTLİS",
    "14": "BOLU",
    "15": "BURDUR",
    "16": "BURSA",
    "17": "ÇANAKKALE",
    "18": "ÇANKIRI",
    "19": "ÇORUM",
    "20": "DENİZLİ",
    "21": "DİYARBAKIR",
    "22": "EDİRNE",
    "23": "ELAZIĞ",
    "24": "ERZİNCAN",
    "25": "ERZURUM",
    "26": "ESKİŞEHİR",
    "27": "GAZİANTEP",
    "28": "GİRESUN",
    "29": "GÜMÜŞHANE",
    "30": "HAKKARİ",
    "31": "HATAY",
    "32": "ISPARTA",
    "33": "MERSİN",
    "34": "İSTANBUL",
    "35": "İZMİR",
    "36": "KARS",
    "37": "KASTAMONU",
    "38": "KAYSERİ",
    "39": "KIRKLARELİ",
    "40": "KIRŞEHİR",
    "41": "KOCAELİ",
    "42": "KONYA",
    "43": "KÜTAHYA",
    "44": "MALATYA",
    "45": "MANİSA",
    "46": "KAHRAMANMARAŞ",
    "47": "MARDİN",
    "48": "MUĞLA",
    "49": "MUŞ",
    "50": "NEVŞEHİR",
    "51": "NİĞDE",
    "52": "ORDU",
    "53": "RİZE",
    "54": "SAKARYA",
    "55": "SAMSUN",
    "56": "SİİRT",
    "57": "SİNOP",
    "58": "SİVAS",
    "59": "TEKİRDAĞ",
    "60": "TOKAT",
    "61": "TRABZON",
    "62": "TUNCELİ",
    "63": "ŞANLIURFA",
    "64": "UŞAK",
    "65": "VAN",
    "66": "YOZGAT",
    "67": "ZONGULDAK",
    "68": "AKSARAY",
    "69": "BAYBURT",
    "70": "KARAMAN",
    "71": "KIRIKKALE",
    "72": "BATMAN",
    "73": "ŞIRNAK",
    "74": "BARTIN",
    "75": "ARDAHAN",
    "76": "IĞDIR",
    "77": "YALOVA",
    "78": "KARABüK",
    "79": "KİLİS",
    "80": "OSMANİYE",
    "81": "DÜZCE"
}
@transaction.atomic
def createCities():
    for i in cities:
        city = City.objects.filter(id=i)
        if not city:
            City.objects.create(name=cities[i],id=i)

createCities()

