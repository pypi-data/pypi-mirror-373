# ረዳት ቤተ መጻሕፍት

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE) [![PyPI](https://img.shields.io/pypi/v/pyhelper-tools-jbhm?style=for-the-badge&label=PyPI&color=blue)](https://pypi.org/project/pyhelper-tools-jbhm/)

## 🌍 የሚገኙ ቋንቋዎች

PYHELEPER እስከ QUIDS ድረስ የተገነባ የትርጓሜዎችን ያቀርባል: -

[![en](https://img.shields.io/badge/lang-en-red.svg)](readme/README.md) [![es](https://img.shields.io/badge/lang-es-yellow.svg)](readme/README.es.md) [![fr](https://img.shields.io/badge/lang-fr-blue.svg)](readme/README.fr.md) [![ru](https://img.shields.io/badge/lang-ru-purple.svg)](readme/README.ru.md) [![ru](https://img.shields.io/badge/lang-ru-purple.svg)](readme/README.ru.md) [![ru](https://img.shields.io/badge/lang-ru-purple.svg)](readme/README.ru.md) [![zh](https://img.shields.io/badge/lang-zh-black.svg)](readme/README.zh.md) [![zh](https://img.shields.io/badge/lang-zh-black.svg)](readme/README.zh.md) [![it](https://img.shields.io/badge/lang-it-lightgrey.svg)](readme/README.it.md) [![pt](https://img.shields.io/badge/lang-pt-brightgreen.svg)](readme/README.pt.md) [![pt](https://img.shields.io/badge/lang-pt-brightgreen.svg)](readme/README.pt.md) [![pt](https://img.shields.io/badge/lang-pt-brightgreen.svg)](readme/README.pt.md)  
[![ja](https://img.shields.io/badge/lang-ja-red.svg)](readme/README.ja.md) [![ar](https://img.shields.io/badge/lang-ar-brown.svg)](readme/README.ar.md) [![af](https://img.shields.io/badge/lang-af-orange.svg)](readme/README.af.md) [![am](https://img.shields.io/badge/lang-am-green.svg)](readme/README.am.md) [![am](https://img.shields.io/badge/lang-am-green.svg)](readme/README.am.md) [![am](https://img.shields.io/badge/lang-am-green.svg)](readme/README.am.md) [![as](https://img.shields.io/badge/lang-as-purple.svg)](readme/README.as.md) [![as](https://img.shields.io/badge/lang-as-purple.svg)](readme/README.as.md) [![az](https://img.shields.io/badge/lang-az-lightblue.svg)](readme/README.az.md) [![az](https://img.shields.io/badge/lang-az-lightblue.svg)](readme/README.az.md) [![az](https://img.shields.io/badge/lang-az-lightblue.svg)](readme/README.az.md) [![bm](https://img.shields.io/badge/lang-bm-darkgreen.svg)](readme/README.bm.md)  
[![eu](https://img.shields.io/badge/lang-eu-pink.svg)](readme/README.eu.md) [![be](https://img.shields.io/badge/lang-be-darkblue.svg)](readme/README.be.md) [![bs](https://img.shields.io/badge/lang-bs-purple.svg)](readme/README.bm.md) [![bs](https://img.shields.io/badge/lang-bs-purple.svg)](readme/README.bm.md) [![bs](https://img.shields.io/badge/lang-bs-purple.svg)](readme/README.bm.md) [![ca](https://img.shields.io/badge/lang-ca-yellow.svg)](readme/README.ca.md) [![ca](https://img.shields.io/badge/lang-ca-yellow.svg)](readme/README.ca.md) [![ca](https://img.shields.io/badge/lang-ca-yellow.svg)](readme/README.ca.md) [![ny](https://img.shields.io/badge/lang-ny-red.svg)](readme/README.ny.md) [![ny](https://img.shields.io/badge/lang-ny-red.svg)](readme/README.ny.md)  
[![hr](https://img.shields.io/badge/lang-hr-blue.svg)](readme/README.hr.md) [![cs](https://img.shields.io/badge/lang-cs-red.svg)](readme/README.cs.md) [![da](https://img.shields.io/badge/lang-da-purple.svg)](readme/README.da.md) [![doi](https://img.shields.io/badge/lang-doi-brown.svg)](readme/README.doi.md) [![doi](https://img.shields.io/badge/lang-doi-brown.svg)](readme/README.doi.md) [![doi](https://img.shields.io/badge/lang-doi-brown.svg)](readme/README.doi.md) [![eo](https://img.shields.io/badge/lang-eo-green.svg)](readme/README.eo.md) [![doi](https://img.shields.io/badge/lang-doi-brown.svg)](readme/README.doi.md) [![doi](https://img.shields.io/badge/lang-doi-brown.svg)](readme/README.doi.md) `` π_131 [![tl](https://img.shields.io/badge/lang-tl-purple.svg)](readme/README.tl.md)  
[![fi](https://img.shields.io/badge/lang-fi-blue.svg)](readme/README.fi.md) [![fy](https://img.shields.io/badge/lang-fy-orange.svg)](readme/README.fy.md) [![gl](https://img.shields.io/badge/lang-gl-green.svg)](readme/README.gl.md) [![el](https://img.shields.io/badge/lang-el-blue.svg)](readme/README.el.md) [![el](https://img.shields.io/badge/lang-el-blue.svg)](readme/README.el.md) [![el](https://img.shields.io/badge/lang-el-blue.svg)](readme/README.el.md) [![el](https://img.shields.io/badge/lang-el-blue.svg)](readme/README.el.md) [![gu](https://img.shields.io/badge/lang-gu-orange.svg)](readme/README.gu.md) [![el](https://img.shields.io/badge/lang-el-blue.svg)](readme/README.el.md) [![el](https://img.shields.io/badge/lang-el-blue.svg)](readme/README.el.md) ```python
import helper as hp

data = [1, 2, 2, 3, 4, 5]

print(hp.get_media(data))   # Mean
print(hp.get_median(data))  # Median
print(hp.get_moda(data))    # Mode
``````python
import helper as hp

data = [1, 2, 2, 3, 4, 5]

print(hp.get_media(data))   # Mean
print(hp.get_median(data))  # Median
print(hp.get_moda(data))    # Mode
```  
```python
from helper import call

data = call(name="my_data", type="csv")  # Finds and loads a CSV file automatically
``` [![hi](https://img.shields.io/badge/lang-hi-orange.svg)](readme/README.hi.md) [![is](https://img.shields.io/badge/lang-is-red.svg)](readme/README.is.md) [![is](https://img.shields.io/badge/lang-is-red.svg)](readme/README.is.md) [![is](https://img.shields.io/badge/lang-is-red.svg)](readme/README.is.md) [![ilo](https://img.shields.io/badge/lang-ilo-orange.svg)](readme/README.ilo.md) [![ilo](https://img.shields.io/badge/lang-ilo-orange.svg)](readme/README.ilo.md) [![ga](https://img.shields.io/badge/lang-ga-blue.svg)](readme/README.ga.md) [![ga](https://img.shields.io/badge/lang-ga-blue.svg)](readme/README.ga.md) π_112 _111_  
[![kn](https://img.shields.io/badge/lang-kn-purple.svg)](readme/README.kn.md) [![kn](https://img.shields.io/badge/lang-kn-purple.svg)](readme/README.kn.md) [![gom](https://img.shields.io/badge/lang-gom-red.svg)](readme/README.gom.md) [![gom](https://img.shields.io/badge/lang-gom-red.svg)](readme/README.gom.md) [![rw](https://img.shields.io/badge/lang-rw-blue.svg)](readme/README.rw.md) [![gom](https://img.shields.io/badge/lang-gom-red.svg)](readme/README.gom.md) [![gom](https://img.shields.io/badge/lang-gom-red.svg)](readme/README.gom.md) [![kri](https://img.shields.io/badge/lang-kri-orange.svg)](readme/README.kri.md) [![kri](https://img.shields.io/badge/lang-kri-orange.svg)](readme/README.kri.md) [![ku](https://img.shields.io/badge/lang-ku-green.svg)](readme/README.ku.md) [![ckb](https://img.shields.io/badge/lang-ckb-blue.svg)](readme/README.ckb.md) [![ckb](https://img.shields.io/badge/lang-ckb-blue.svg)](readme/README.ckb.md) [![ky](https://img.shields.io/badge/lang-ky-red.svg)](readme/README.ky.md)  
[![lo](https://img.shields.io/badge/lang-lo-purple.svg)](readme/README.lo.md) [![la](https://img.shields.io/badge/lang-la-orange.svg)](readme/README.la.md) [![lv](https://img.shields.io/badge/lang-lv-green.svg)](readme/README.lv.md) [![lt](https://img.shields.io/badge/lang-lt-red.svg)](readme/README.lt.md) [![lt](https://img.shields.io/badge/lang-lt-red.svg)](readme/README.lt.md) [![lt](https://img.shields.io/badge/lang-lt-red.svg)](readme/README.lt.md) [![lt](https://img.shields.io/badge/lang-lt-red.svg)](readme/README.lt.md) [![lb](https://img.shields.io/badge/lang-lb-orange.svg)](readme/README.lb.md) [![lb](https://img.shields.io/badge/lang-lb-orange.svg)](readme/README.lb.md) [![mk](https://img.shields.io/badge/lang-mk-green.svg)](readme/README.mk.md) [![mk](https://img.shields.io/badge/lang-mk-green.svg)](readme/README.mk.md) [![mai](https://img.shields.io/badge/lang-mai-blue.svg)](readme/README.mai.md) π_92 _91_  
[![ms](https://img.shields.io/badge/lang-ms-purple.svg)](readme/README.ms.md) [![mr](https://img.shields.io/badge/lang-mr-red.svg)](readme/README.mr.md) [![mt](https://img.shields.io/badge/lang-mt-green.svg)](readme/README.mt.md) [![mr](https://img.shields.io/badge/lang-mr-red.svg)](readme/README.mr.md) [![mr](https://img.shields.io/badge/lang-mr-red.svg)](readme/README.mr.md) [![mr](https://img.shields.io/badge/lang-mr-red.svg)](readme/README.mr.md) [![mr](https://img.shields.io/badge/lang-mr-red.svg)](readme/README.mr.md) [![mn](https://img.shields.io/badge/lang-mn-orange.svg)](readme/README.mn.md) [![my](https://img.shields.io/badge/lang-my-green.svg)](readme/README.my.md) π_8.18 12_ [![no](https://img.shields.io/badge/lang-no-red.svg)](readme/README.no.md) [![no](https://img.shields.io/badge/lang-no-red.svg)](readme/README.no.md)  
[![om](https://img.shields.io/badge/lang-om-orange.svg)](readme/README.om.md) [![qu](https://img.shields.io/badge/lang-qu-red.svg)](readme/README.qu.md) [![fa](https://img.shields.io/badge/lang-fa-blue.svg)](readme/README.fa.md) [![qu](https://img.shields.io/badge/lang-qu-red.svg)](readme/README.qu.md) [![qu](https://img.shields.io/badge/lang-qu-red.svg)](readme/README.qu.md) [![ro](https://img.shields.io/badge/lang-ro-purple.svg)](readme/README.ro.md) [![sm](https://img.shields.io/badge/lang-sm-orange.svg)](readme/README.sm.md) [![sa](https://img.shields.io/badge/lang-sa-green.svg)](readme/README.sa.md) [![sa](https://img.shields.io/badge/lang-sa-green.svg)](readme/README.sa.md) [![gd](https://img.shields.io/badge/lang-gd-blue.svg)](readme/README.gd.md) [![nso](https://img.shields.io/badge/lang-nso-red.svg)](readme/README.nso.md) [![nso](https://img.shields.io/badge/lang-nso-red.svg)](readme/README.nso.md) [![nso](https://img.shields.io/badge/lang-nso-red.svg)](readme/README.nso.md) [![nso](https://img.shields.io/badge/lang-nso-red.svg)](readme/README.nso.md) [![ta](https://img.shields.io/badge/lang-ta-purple.svg)](readme/README.ta.md) [![ta](https://img.shields.io/badge/lang-ta-purple.svg)](readme/README.ta.md) [![sn](https://img.shields.io/badge/lang-sn-orange.svg)](readme/README.sn.md)  
[![sd](https://img.shields.io/badge/lang-sd-green.svg)](readme/README.sd.md) [![si](https://img.shields.io/badge/lang-si-blue.svg)](readme/README.si.md) [![sk](https://img.shields.io/badge/lang-sk-red.svg)](readme/README.sk.md) [![sk](https://img.shields.io/badge/lang-sk-red.svg)](readme/README.sk.md) [![sk](https://img.shields.io/badge/lang-sk-red.svg)](readme/README.sk.md) [![so](https://img.shields.io/badge/lang-so-orange.svg)](readme/README.so.md) [![su](https://img.shields.io/badge/lang-su-green.svg)](readme/README.su.md) [![sw](https://img.shields.io/badge/lang-sw-blue.svg)](readme/README.sw.md) [![tg](https://img.shields.io/badge/lang-tg-red.svg)](readme/README.tg.md) π61_ π61_ π61_ π66_ [![tt](https://img.shields.io/badge/lang-tt-orange.svg)](readme/README.tt.md) [![te](https://img.shields.io/badge/lang-te-green.svg)](readme/README.te.md)  
[![th](https://img.shields.io/badge/lang-th-blue.svg)](readme/README.th.md) [![ti](https://img.shields.io/badge/lang-ti-red.svg)](readme/README.ti.md) [![ti](https://img.shields.io/badge/lang-ti-red.svg)](readme/README.ti.md) [![tk](https://img.shields.io/badge/lang-tk-orange.svg)](readme/README.tk.md) [![tk](https://img.shields.io/badge/lang-tk-orange.svg)](readme/README.tk.md) [![ak](https://img.shields.io/badge/lang-ak-green.svg)](readme/README.ak.md) [![uk](https://img.shields.io/badge/lang-uk-blue.svg)](readme/README.uk.md) [![ur](https://img.shields.io/badge/lang-ur-red.svg)](readme/README.ur.md) [![ur](https://img.shields.io/badge/lang-ur-red.svg)](readme/README.ur.md) [![sn](https://img.shields.io/badge/lang-sn-orange.svg)](readme/README.sn.md) [![sn](https://img.shields.io/badge/lang-sn-orange.svg)](readme/README.sn.md) [![sd](https://img.shields.io/badge/lang-sd-green.svg)](readme/README.sd.md) [![xh](https://img.shields.io/badge/lang-xh-red.svg)](readme/README.xh.md)  
[![xh](https://img.shields.io/badge/lang-xh-red.svg)](readme/README.xh.md) [![yi](https://img.shields.io/badge/lang-yi-purple.svg)](readme/README.yi.md) [![yo](https://img.shields.io/badge/lang-yo-orange.svg)](readme/README.yo.md) [![zu](https://img.shields.io/badge/lang-zu-green.svg)](readme/README.zu.md)

---


## 🚀 ጭነት

ከ PYPI ይጫኑት

```bash
pip install pyhelper-tools-jbhm
```

---

## 📖 አጠቃላይ እይታ

** pyhely ** ቀለል ለማድረግ የተነደፈ ሁለገብ Python መሣሪያ ነው ** የመረጃ ትንተና, የዓይን ትንታኔ, ስታቲስቲካዊ ስራዎች እና የፍጆታ የሥራ ስምሪት ** .  
ከቦሊፕልክ ኮድ ይልቅ በክስተቶች ላይ እንዲያተኩሩ በመፍቀድ በአካዴሚያዊ, ምርምር, እና ሙያዊ ፕሮጀክቶች ውስጥ ያተኮረ ነው.

ቁልፍ ጥቅሞች
- 🧮 አብሮገነብ - ስታቲስቲክስ እና የሂሳብ መገልገያዎች **
- 📊 ለአጠቃቀም ቀላል ** የመረጃ እይታ መጠቅለያ መጠቅለያ ** 
- 🗂 አንድ ምቹ ** ፋይል አያያዝ እና መፈለግ ** 
- 🔍 ** አመልካች ማረጋገጫ ማረጋገጫ ** ለ Python ፋይሎች
- 🌍 ** ባለብዙ ቋንቋ ድጋፍ ** ዝግጁ-በተዘጋጁ ትርጉሞች
- 🚀 ለ <ፈጣን >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

---

## ✨ ቁልፍ ባህሪዎች

### 📊 የውሂብ እይታ
- አሞሌ ገበታዎች አግድም እና ቀጥ ያለ (`hbar`, `vbar`)  
- ስርጭት እሽቅድምድም: - ሂስቶግራም (`histo`), የቦክስ ማቅረቢያዎች (`boxplot`), KDE POLE Po(`kdeplot`)  
- የንፅፅር ማቅረቢያዎች: ቫዮሊን, መንጋዎች, ክሬስ ማቅረቢያዎች  
- የክብደት ትንታኔ-የሙቀት አማቲዎች (`heatmap`), የተበታተኑ POOS _34_  
- የተራቀቁ ልዩነቶች: ጥንድ ማቅረቢያ, የጋራ ማቅረቢያዎች, የቁጥሮች ቅሬታዎች  
- የውሂብ ሠንጠረ at ች: ቅርጸት የተሰሩ ሰንጠረዥ ማሳያዎች (`table`)  

### 📈 ስታቲስቲካዊ ትንታኔ
- ** ማዕከላዊ ዝንባሌ ** : አማካኝ (`get_media`), መካከለኛ _31_, ሁነታዎች (`get_moda`)  
- ** መዘርጋት ** : - ክልል (`get_rank`), ልዩነት (`get_var`), መደበኛ መዛባት (`get_desv`)  
- ** ትንታኔ ** : የተበታተኑ ሪፖርቶች (`disp`), IQR ስሌቶች, መደበኛ አቀማመጥ, ሁኔታዊ ለውጥ  
- ** የአፋጣኝ መመርመር ** : IQR እና Z- ውጤት ዘዴዎች  

### 🗂️ የፋይል አስተዳደር
- ዘመናዊ ግኝት ከ `call()` (auto-detect CSV, JSON, XML, etc.) ጋር  
- ባለብዙ ቅርጸት ድጋፍ (CSV, JSON, XML, PDF, spatial data)  
- የ SQL የመረጃ ቋት አያያዝ ከ `DataBase` ክፍል ጋር  
- የውይይት መገልገያዎች (`convert_file`)  

### 🛠️ የገንቢ መሣሪያዎች
- የመቀየር ስርዓት _20_  
- አገባብ ቼክ (`check_syntax`, `PythonFileChecker`)  
- ሀብታም ስህተት ሪፖርት ማድረግ (multi-language)  
- የተቀናጀ የእገዛ ስርዓት (`help`)  

### 🌍 ዓለም አቀፍ
- 100+ የተገነቡ ትርጉሞች  
- ብጁ ትርጉሞችን ይጭኑ  
- የአሮጌ ጊዜ ቋንቋ ማዞሪያ (`set_language()1_15_1π`python
from helper import set_language

set_language("en")  # English
set_language("es")  # Spanish
set_language("fr")  # French
set_language("de")  # German
set_language("ru")  # Russian
set_language("tr")  # Turkish
set_language("zh")  # Chinese
set_language("it")  # Italian
set_language("pt")  # Portuguese
set_language("sv")  # Swedish
set_language("ja")  # Japanese
set_language("ar")  # Arabic
...
`1_13_


### መሠረታዊ ስታቲስቲክስ
```python
import helper as hp

data = [1, 2, 2, 3, 4, 5]

print(hp.get_media(data))   # Mean
print(hp.get_median(data))  # Median
print(hp.get_moda(data))    # Mode
```

### የእይታ እይታ
```python
import helper as hp

df = hp.pd.DataFrame({"values": [5, 3, 7, 2, 9]})
hp.histo(df, "values", bins=5, title="Sample Histogram")
```

### ፋይል አያያዝ
```python
from helper import call

data = call(name="my_data", type="csv")  # Finds and loads a CSV file automatically
```

### ብጁ ትርጉሞች
```python
from helper import load_user_translations

# Load custom translations from lang.json
load_user_translations("custom/lang.json")
```

### አገባብ ማረጋገጫ
```python
from helper import run

run("./path/to/my_script.py")
#Show gui pop up with results
```

---

## 📂 የፕሮጀክት መዋቅር

```
helper/
├── core.py
├── __init__.py
├── lang/
│   ├── en.json
│   ├── es.json
│   └── ... (100+ files)
└── submodules/
    ├── graph.py
    ├── statics.py
    ├── utils.py
    ├── caller.py
    ├── checker.py
    ├── manager.py
    ├── pyswitch.py
    ├── shared.py
    └── DBManager.py
```

---

## 📜 📜 📜_6_

ይህ ፕሮጀክት ከ **_6_ π_6 _4 _ * ** **.  
ለዝርዝሮች [LICENSE](LICENSE) ፋይልን ይመልከቱ.

---

## 🔮 ጎዳና

- ተጨማሪ የአመለካከት ዓይነቶች

- የተራዘመ የውሂብ ጎታ ድጋፍ (NoSQL, graph databases)

- የማሽን ትምህርት ውህደት

- በዌ-ተኮር በይነገጽ

- ተሰኪ ስርዓት

---

⚡ __1_ የሥራ ቅሎዎችዎን ከፋይሉ ** pylluper ** passlyly ለማሟላት ዝግጁ ነዎት? ዛሬ ማሰስ ይጀምሩ!