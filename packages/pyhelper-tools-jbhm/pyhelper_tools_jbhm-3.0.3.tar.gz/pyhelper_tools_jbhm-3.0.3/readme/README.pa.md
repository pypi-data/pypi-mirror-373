# ਮਦਦਗਾਰ ਲਾਇਬ੍ਰੇਰੀ

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE) [![PyPI](https://img.shields.io/pypi/v/pyhelper-tools-jbhm?style=for-the-badge&label=PyPI&color=blue)](https://pypi.org/project/pyhelper-tools-jbhm/)

## 🌍 ਉਪਲਬਧ ਭਾਸ਼ਾਵਾਂ

** 131 ਭਾਸ਼ਾਵਾਂ ** ਲਈ ਥਾਈਲੈਫਰ ਬਿਲਟ-ਇਨ ਅਨੁਵਾਦ ਪੇਸ਼ ਕਰਦਾ ਹੈ * ਜਿਵੇਂ ਕਿ:

[![en](https://img.shields.io/badge/lang-en-red.svg)](readme/README.md) [![de](https://img.shields.io/badge/lang-de-green.svg)](readme/README.de.md) [![ru](https://img.shields.io/badge/lang-ru-purple.svg)](readme/README.ru.md) [![ru](https://img.shields.io/badge/lang-ru-purple.svg)](readme/README.ru.md) [![it](https://img.shields.io/badge/lang-it-lightgrey.svg)](readme/README.it.md) [![it](https://img.shields.io/badge/lang-it-lightgrey.svg)](readme/README.it.md) [![it](https://img.shields.io/badge/lang-it-lightgrey.svg)](readme/README.it.md) [![sv](https://img.shields.io/badge/lang-sv-blue.svg)](readme/README.sv.md)  
`)  
- Automatic English fallback  

---

## Dependencies (handled automatically):

- pandas, numpy (data manipulation)

- matplotlib, seaborn (visualization)

- scikit-learn (statistics)

- sqlalchemy (database)

- geopandas (spatial data)

---

## 🔧 Usage Examples

### Set language 

**support for up to 131 languages** 
` [![sq](https://img.shields.io/badge/lang-sq-blue.svg)](readme/README.sq.md) π_156 [![hy](https://img.shields.io/badge/lang-hy-red.svg)](readme/README.hy.md) [![ay](https://img.shields.io/badge/lang-ay-brown.svg)](readme/README.ay.md) [![az](https://img.shields.io/badge/lang-az-lightblue.svg)](readme/README.az.md) [![bm](https://img.shields.io/badge/lang-bm-darkgreen.svg)](readme/README.bm.md)  
(`set_language() [![be](https://img.shields.io/badge/lang-be-darkblue.svg)](readme/README.be.md) [![bho](https://img.shields.io/badge/lang-bho-orange.svg)](readme/README.bho.md) [![bg](https://img.shields.io/badge/lang-bg-green.svg)](readme/README.bg.md) [![ceb](https://img.shields.io/badge/lang-ceb-blue.svg)](readme/README.ceb.md) [![ny](https://img.shields.io/badge/lang-ny-red.svg)](readme/README.ny.md) [![ny](https://img.shields.io/badge/lang-ny-red.svg)](readme/README.ny.md)  
[![hr](https://img.shields.io/badge/lang-hr-blue.svg)](readme/README.hr.md) [![da](https://img.shields.io/badge/lang-da-purple.svg)](readme/README.da.md) [![doi](https://img.shields.io/badge/lang-doi-brown.svg)](readme/README.doi.md) [![nl](https://img.shields.io/badge/lang-nl-orange.svg)](readme/README.nl.md) [![et](https://img.shields.io/badge/lang-et-blue.svg)](readme/README.et.md) [![et](https://img.shields.io/badge/lang-et-blue.svg)](readme/README.et.md) [![et](https://img.shields.io/badge/lang-et-blue.svg)](readme/README.et.md) [![ee](https://img.shields.io/badge/lang-ee-red.svg)](readme/README.ee.md) [![tl](https://img.shields.io/badge/lang-tl-purple.svg)](readme/README.tl.md)  
[![fy](https://img.shields.io/badge/lang-fy-orange.svg)](readme/README.fy.md) [![fy](https://img.shields.io/badge/lang-fy-orange.svg)](readme/README.fy.md) [![gn](https://img.shields.io/badge/lang-gn-purple.svg)](readme/README.gn.md) [![gn](https://img.shields.io/badge/lang-gn-purple.svg)](readme/README.gn.md) [![ht](https://img.shields.io/badge/lang-ht-green.svg)](readme/README.ht.md) [![ha](https://img.shields.io/badge/lang-ha-blue.svg)](readme/README.ha.md)  
```python
import helper as hp

df = hp.pd.DataFrame({"values": [5, 3, 7, 2, 9]})
hp.histo(df, "values", bins=5, title="Sample Histogram")
``` [![hu](https://img.shields.io/badge/lang-hu-blue.svg)](readme/README.hu.md) [![is](https://img.shields.io/badge/lang-is-red.svg)](readme/README.is.md) [![ig](https://img.shields.io/badge/lang-ig-purple.svg)](readme/README.ig.md) [![id](https://img.shields.io/badge/lang-id-green.svg)](readme/README.id.md) [![id](https://img.shields.io/badge/lang-id-green.svg)](readme/README.id.md) [![ga](https://img.shields.io/badge/lang-ga-blue.svg)](readme/README.ga.md)  
[![kn](https://img.shields.io/badge/lang-kn-purple.svg)](readme/README.kn.md) [![rw](https://img.shields.io/badge/lang-rw-blue.svg)](readme/README.rw.md) [![gom](https://img.shields.io/badge/lang-gom-red.svg)](readme/README.gom.md) [![kri](https://img.shields.io/badge/lang-kri-orange.svg)](readme/README.kri.md) [![ku](https://img.shields.io/badge/lang-ku-green.svg)](readme/README.ku.md) [![ckb](https://img.shields.io/badge/lang-ckb-blue.svg)](readme/README.ckb.md) [![ckb](https://img.shields.io/badge/lang-ckb-blue.svg)](readme/README.ckb.md)  
[![lo](https://img.shields.io/badge/lang-lo-purple.svg)](readme/README.lo.md) [![lt](https://img.shields.io/badge/lang-lt-red.svg)](readme/README.lt.md) [![lt](https://img.shields.io/badge/lang-lt-red.svg)](readme/README.lt.md) [![lt](https://img.shields.io/badge/lang-lt-red.svg)](readme/README.lt.md) [![mk](https://img.shields.io/badge/lang-mk-green.svg)](readme/README.mk.md) [![mai](https://img.shields.io/badge/lang-mai-blue.svg)](readme/README.mai.md) [![mg](https://img.shields.io/badge/lang-mg-red.svg)](readme/README.mg.md)  
[![ms](https://img.shields.io/badge/lang-ms-purple.svg)](readme/README.ms.md) [![mt](https://img.shields.io/badge/lang-mt-green.svg)](readme/README.mt.md) [![mr](https://img.shields.io/badge/lang-mr-red.svg)](readme/README.mr.md) [![mr](https://img.shields.io/badge/lang-mr-red.svg)](readme/README.mr.md) [![mr](https://img.shields.io/badge/lang-mr-red.svg)](readme/README.mr.md) [![ne](https://img.shields.io/badge/lang-ne-blue.svg)](readme/README.ne.md) [![ne](https://img.shields.io/badge/lang-ne-blue.svg)](readme/README.ne.md) [![no](https://img.shields.io/badge/lang-no-red.svg)](readme/README.no.md) [![or](https://img.shields.io/badge/lang-or-purple.svg)](readme/README.or.md)  
[![om](https://img.shields.io/badge/lang-om-orange.svg)](readme/README.om.md) [![qu](https://img.shields.io/badge/lang-qu-red.svg)](readme/README.qu.md) [![qu](https://img.shields.io/badge/lang-qu-red.svg)](readme/README.qu.md) [![qu](https://img.shields.io/badge/lang-qu-red.svg)](readme/README.qu.md) [![sa](https://img.shields.io/badge/lang-sa-green.svg)](readme/README.sa.md) [![gd](https://img.shields.io/badge/lang-gd-blue.svg)](readme/README.gd.md) [![st](https://img.shields.io/badge/lang-st-purple.svg)](readme/README.st.md) [![sn](https://img.shields.io/badge/lang-sn-orange.svg)](readme/README.sn.md)  
[![sd](https://img.shields.io/badge/lang-sd-green.svg)](readme/README.sd.md) [![sk](https://img.shields.io/badge/lang-sk-red.svg)](readme/README.sk.md) [![sk](https://img.shields.io/badge/lang-sk-red.svg)](readme/README.sk.md) [![su](https://img.shields.io/badge/lang-su-green.svg)](readme/README.su.md) [![sw](https://img.shields.io/badge/lang-sw-blue.svg)](readme/README.sw.md) [![sw](https://img.shields.io/badge/lang-sw-blue.svg)](readme/README.sw.md) License [![ti](https://img.shields.io/badge/lang-ti-red.svg)](readme/README.ti.md) [![te](https://img.shields.io/badge/lang-te-green.svg)](readme/README.te.md)  
[![th](https://img.shields.io/badge/lang-th-blue.svg)](readme/README.th.md) [![ti](https://img.shields.io/badge/lang-ti-red.svg)](readme/README.ti.md) [![ti](https://img.shields.io/badge/lang-ti-red.svg)](readme/README.ti.md) [![uk](https://img.shields.io/badge/lang-uk-blue.svg)](readme/README.uk.md) MIT MIT [![uz](https://img.shields.io/badge/lang-uz-orange.svg)](readme/README.uz.md) [![vi](https://img.shields.io/badge/lang-vi-green.svg)](readme/README.vi.md) [![cy](https://img.shields.io/badge/lang-cy-blue.svg)](readme/README.cy.md)  
[![xh](https://img.shields.io/badge/lang-xh-red.svg)](readme/README.xh.md) [![yi](https://img.shields.io/badge/lang-yi-purple.svg)](readme/README.yi.md) [![zu](https://img.shields.io/badge/lang-zu-green.svg)](readme/README.zu.md) [![zu](https://img.shields.io/badge/lang-zu-green.svg)](readme/README.zu.md)

---


## 🚀 ਇੰਸਟਾਲੇਸ਼ਨ

ਪਾਈਪੀਆਈ ਤੋਂ ਸਥਾਪਿਤ ਕਰੋ:

```bash
pip install pyhelper-tools-jbhm
```

---

## 📖 ਸੰਖੇਪ ਜਾਣਕਾਰੀ

** ਪਾਇਹਲਪਰ ** ਸਰਲ ਬਣਾਉਣ ਲਈ ਤਿਆਰ ਕੀਤਾ ਗਿਆ ਇਕ ਬਹੁਪੱਖੀ Python ਟੂਲਕਿੱਟ ਹੈ ** ਡਾਟਾ ਵਿਸ਼ਲੇਸ਼ਣ, ਵਿਜ਼ੂਅਲੇਸ਼ਨ, ਅੰਕੜਾ ਓਪਰੇਸ਼ਨਾਂ ਅਤੇ ਸਹੂਲਤ ਵਰਕਫ੍ਰੋਜ ** .  
ਇਹ ਨਿਰਾਦਰਿਕ, ਖੋਜ ਅਤੇ ਪੇਸ਼ੇਵਰ ਪ੍ਰਾਜੈਕਟਾਂ ਵਿੱਚ ਨਿਰਵਿਘਨ ਏਕੀਕ੍ਰਿਤ ਕਰਦਾ ਹੈ, ਜਿਸ ਨਾਲ ਤੁਸੀਂ ਬਾਇਲਰ ਪਲੇਟ ਕੋਡ ਦੀ ਬਜਾਏ ਇਨਸਾਈਟਸ ਤੇ ਧਿਆਨ ਕੇਂਦਰਤ ਕਰਦੇ ਹੋ.

ਮੁੱਖ ਫਾਇਦੇ:
- 🧮 ਬਿਲਟ-ਇਨ ** ਅੰਕੜੇ ਅਤੇ ਗਣਿਤ ਸਹੂਲਤਾਂ ** 
- 📊 ਆਸਾਨ-ਟੂ-ਵਰਤੋਂ ** ਡਾਟਾ ਵਿਜ਼ੂਅਲਾਈਜ਼ੇਸ਼ਨ ਰੈਪਰਜ਼ ** 
- 🗂 ਹੈਂਡਸੀ ** ਫਾਈਲ ਹੈਂਡਲਿੰਗ ਅਤੇ ਖੋਜ ਕਰ ਰਹੇ ਹੋ ** 
- 🔍 ** ਸਿੰਟੈਕਸ ਪ੍ਰਮਾਣਿਕਤਾ ** Python ਫਾਈਲਾਂ ਲਈ
- 🌍 ** ਮਲਟੀ-ਲੈਂਗਵੇਜ਼ ਸਹਾਇਤਾ ** ਤਿਆਰ ਅਨੁਵਾਦ ਦੇ ਨਾਲ
- ** ਫਾਸਟ ਪ੍ਰੋਟੋਟਿੰਗ ** ਅਤੇ ** ਸਿੱਖਿਆ ** 

---

## ✨ ਮੁੱਖ ਵਿਸ਼ੇਸ਼ਤਾਵਾਂ

### 📊 ਡਾਟਾ ਵਿਜ਼ੂਅਲਾਈਜ਼ੇਸ਼ਨ
- ਬਾਰ ਚਾਰਟ: ਹਰੀਜ਼ਟਲ ਅਤੇ ਵਰਟੀਕਲ (`hbar`, `vbar`)  
- ਵੰਡ ਪਲਾਟ: ਹਿਸਟੋਗ੍ਰਾਮ (`histo`), ਬਾਕਸ ਪਲਾਟ (`boxplot`), ਕੇਡੀਈ ਪਲਾਟਾਂ (`kdeplot`)  
- ਤੁਲਨਾਤਮਕ ਪਲਾਟ: ਵਾਇਲਨ, ਸਵਰਮ, ਸਟਰਿੱਪ ਪਲਾਟ  
- ਸੰਬੰਧ ਵਿਸ਼ਲੇਸ਼ਣ: ਹੀਟਮੈਪਸ (`heatmap`), ਸਕੈਟਰ ਪਲਾਟਾਂ (`scatter`)  
- ਉੱਨਤ ਦਰਿਸ਼: ਜੋੜਾ ਪਲਾਟ, ਸੰਯੁਕਤ ਪਲਾਟ, ਰੈਗ੍ਰੇਸ਼ਨ ਪਲਾਟ  
- ਡਾਟਾ ਟੇਬਲ: ਫਾਰਮੈਟਡ ਟੇਬਲ ਡਿਸਪਲੇਅ (`table`)  

### 📈 ਅੰਕੜਾ ਵਿਸ਼ਲੇਸ਼ਣ
- ** ਕੇਂਦਰੀ ਰੁਝਾਨ ** : ਮਤਲਬ (`get_media`), ਮੀਡੀਅਨ (`get_median`), ਮੋਡ (`get_moda`)  
- ** ਫੈਲਾਓ ** : ਸੀਮਾ (`get_rank`), ਪਰਿਵਰਤਨ (`get_var`), ਮਿਆਰੀ ਭਟਕਣਾ (`get_desv`)  
- ** ਵਿਸ਼ਲੇਸ਼ਣ ** : ਫੈਲਾਓ ਰਿਪੋਰਟ (`disp`), ਆਈਕਿਯੂਆਰ ਗਣਨਾ, ਸਧਾਰਣਕਰਣ, ਸ਼ਰਤੀਆ ਤਬਦੀਲੀ  
- ** ਆਉਟਰੀਲਿਟਡ ਖੋਜ ** : ਆਈਕਿਯੂਆਰ ਅਤੇ ਜ਼ੈਡ-ਸਕੋਰ .ੰਗ  

### 🗂️ ਫਾਈਲ ਪ੍ਰਬੰਧਨ
- `call()` (auto-detect CSV, JSON, XML, etc.) ਨਾਲ ਸਮਾਰਟ ਖੋਜ  
- ਮਲਟੀ-ਫਾਰਮੈਟ ਸਹਾਇਤਾ (CSV, JSON, XML, PDF, spatial data)  
- `DataBase` ਕਲਾਸ ਦੇ ਨਾਲ SQL ਡਾਟਾਬੇਸ ਪ੍ਰਬੰਧਨ  
- ਪਰਿਵਰਤਨ ਸਹੂਲਤਾਂ (`convert_file`)  

### 🛠️ ਡਿਵੈਲਪਰ ਟੂਲ
- ਸਵਿੱਚ ਸਿਸਟਮ (`Switch`, `AsyncSwitch`)  
- ਸਿੰਟੈਕਸ ਚੈਕਿੰਗ (`check_syntax`, `PythonFileChecker`)  
- ਅਮੀਰ ਗਲਤੀ ਰਿਪੋਰਟਿੰਗ (multi-language)  
- ਏਕੀਕ੍ਰਿਤ ਸਹਾਇਤਾ ਸਿਸਟਮ (`help`)  

### 🌍 ਅੰਤਰਰਾਸ਼ਟਰੀਕਰਨ
- 100+ ਬਿਲਟ-ਇਨ ਅਨੁਵਾਦ  
- ਕਸਟਮ ਅਨੁਵਾਦ ਲੋਡ ਕਰੋ  
- ਰੰਨਟਾਈਮ ਭਾਸ਼ਾ ਸਵਿੱਚਿੰਗ (`set_language() `)  
- Automatic English fallback  

---

## Dependencies (handled automatically):

- pandas, numpy (data manipulation)

- matplotlib, seaborn (visualization)

- scikit-learn (statistics)

- sqlalchemy (database)

- geopandas (spatial data)

---

## 🔧 Usage Examples

### Set language 

**support for up to 131 languages** 
```python
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
`4_13_


### ਮੁ basic ਲੇ ਅੰਕੜੇ
```python
import helper as hp

data = [1, 2, 2, 3, 4, 5]

print(hp.get_media(data))   # Mean
print(hp.get_median(data))  # Median
print(hp.get_moda(data))    # Mode
```

## ਇਹ ਦ੍ਰਿਸ਼ਟੀਕੋਣ
```python
import helper as hp

df = hp.pd.DataFrame({"values": [5, 3, 7, 2, 9]})
hp.histo(df, "values", bins=5, title="Sample Histogram")
```

### ਫਾਈਲ ਹੈਂਡਲਿੰਗ
```python
from helper import call

data = call(name="my_data", type="csv")  # Finds and loads a CSV file automatically
```

### ਕਸਟਮ ਅਨੁਵਾਦ
```python
from helper import load_user_translations

# Load custom translations from lang.json
load_user_translations("custom/lang.json")
```

### ਸੰਟੈਕਸ ਪ੍ਰਮਾਣਿਕਤਾ
```python
from helper import run

run("./path/to/my_script.py")
#Show gui pop up with results
```

---

## 📂 ਪ੍ਰੋਜੈਕਟ ਬਣਤਰ

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

## 📜 License

ਇਹ ਪ੍ਰੋਜੈਕਟ ** MIT π_4 _ ** ਦੇ ਅਧੀਨ ਲਾਇਸੈਂਸਸ਼ੁਦਾ ਹੈ.  
ਵੇਰਵਿਆਂ ਲਈ [LICENSE](LICENSE) ਫਾਈਲ ਵੇਖੋ.

---

## 🔮 ਰੋਡਮੈਪ

- ਵਾਧੂ ਵਿਜ਼ੂਅਲਾਈਜੇਸ਼ਨ ਕਿਸਮਾਂ

- ਐਕਸਟੈਂਡਡ ਡਾਟਾਬੇਸ ਸਪੋਰਟ (NoSQL, graph databases)

- ਮਸ਼ੀਨ ਸਿਖਲਾਈ ਏਕੀਕਰਣ

- ਵੈੱਬ-ਅਧਾਰਤ ਇੰਟਰਫੇਸ

- ਪਲੱਗਇਨ ਸਿਸਟਮ

---

You ** ਪਾਈਹਹਲਪਰ ਦੇ ਨਾਲ ਆਪਣੇ Python ਵਰਕਫਲੋਜ਼ ਸੁਪਰਚਾਰਜ ਕਰਨ ਲਈ ਤਿਆਰ. ਅੱਜ ਦੀ ਪੜਨਾ ਸ਼ੁਰੂ ਕਰੋ!