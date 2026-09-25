# aarch64 Önyüklemesi

Bu dizin Pisi GNU/Linux'u arm64 (`aarch64`) üzerinde sıfırdan kurmanın ilk adımını içerir. Henüz bir Pisi aarch64 sistemi olmadığı için ilk paketler başka bir arm64 dağıtımının üzerinde, PiSi ile derlenir.

## Aşamalar

| Aşama | Ne yapar | Durum |
|---|---|---|
| 0 | Debian arm64 üzerinde Python 2.7 ve PiSi'yi core tariflerinin kendi kaynak ve yamalarıyla kurar. Bu imajdaki `pisi build` emülasyonsuz aarch64 paketi üretir. | Bu dizin |
| 1 | Aşama 0 ile core'daki tarifleri aarch64 paketlerine dönüştürür (`build-stage1.sh`). | 245 tarifin 206'sı derleniyor |
| 2 | Aşama 1 paketlerini boş bir köke kurar, bu Pisi kökünün içinde önce Python 3 derleme zincirini, sonra core'u Pisi'nin kendi araçlarıyla yeniden derler; sonuç, x86-64'teki `pisilinux/chroot` imajının aarch64 karşılığıdır. | Kök ve Python zinciri hazır; core'un yeniden derlenmesi sürüyor |

## Aşama 0'ı hazırlamak

Deponun kökünden:

```sh
scripts/bootstrap/aarch64/prepare.py
docker build --platform linux/arm64 -t pisi-aarch64-stage0 scripts/bootstrap/aarch64/context
```

`prepare.py`, aşağıdaki tariflerin `pspec.xml` dosyalarını okur; her birinin kaynak arşivini indirir, `sha1sum` değerini doğrular ve yamalarını sırasıyla bağlam dizinine kopyalar: python, python-setuptools, python-six, piksemel, python-pyliblzma, cython, plyvel, pycurl, urlgrabber, file ve pisi. Böylece aşama 0 kendi sürümlerini sabitlemez; tariflerde sürüm ya da yama değişince bir sonraki hazırlık onu kullanır. PiSi de `system/base/pisi` tarifinin kurduğu haliyle derlenir (v2.7.2 ve tarifin bütün yamaları, mimari modeli dahil).

`build-stage0.sh` her adımda ilgili tarifin `build()` ve `install()` işlevlerini izler; farklılıklar betikte açıklanmıştır (örneğin Debian'ın GCC 14'ü C17 varsaydığı için Python'un C23 ile derlenmesi).

## Aşama 0'da paket derlemek

```sh
docker run --rm -it --platform linux/arm64 -v "$PWD:/work:ro" pisi-aarch64-stage0
cp -r /work/system/base/which /tmp && cd /tmp/which
pisi bi --ignore-sandbox --ignore-safety --ignore-dependency -y pspec.xml
```

Sonuç `which-2.25-7-p2-aarch64.pisi` gibi aarch64 adlı bir pakettir.

Notlar:

- Derleme bağımlılıkları henüz Pisi paketi olarak bulunmadığı için Debian'dan gelir; `--ignore-dependency` bu yüzden gereklidir.
- PiSi derleyiciyi Pisi triplet'iyle (`aarch64-pc-linux-gnu-gcc`) çağırır; imaj Debian araçlarını bu adlarla da bağlar.
- `mirrors://` adresleri, pisi tarifinden kopyalanan `mirrors.conf` ile çözülür.
- SourceForge tarayıcı kimliğiyle gelen isteklere 403 döner; `prepare.py` bu yüzden PiSi'nin indiricisinin kimliğini kullanır.

## Aşama 1: core'u aarch64 için paketlemek

```sh
docker run -d --name pisi-a64 --platform linux/arm64 \
    -v "$PWD:/work:ro" -v "$PWD/../stage1:/out" pisi-aarch64-stage0 sleep infinity
docker exec pisi-a64 /work/scripts/bootstrap/aarch64/build-stage1.sh [tarif ...]
```

Tarif verilmezse depodaki bütün tarifler derlenir. Paketler `/out/packages`, günlükler `/out/logs`, tarif başına bir sonuç satırı `/out/status` altına yazılır (`PASS`, `FAIL`, `EXCLUDED`). Başarılı tarifler yeniden çalıştırmada atlanır; hatalar düzeltildikçe betik tekrar çalıştırılabilir. `ExcludeArch` taşıyan x86'ya özel paketler `EXCLUDED` olarak işaretlenir, emul32 (32 bit) paketleri aarch64'te derlenmez. Testler bu aşamada atlanır; aşama 2'de, Pisi'nin kendi kütüphaneleriyle yeniden derlenirken çalıştırılır.

Aşama 1'de tarifler Debian'ın araçları ve başlıklarıyla derlenir; bu yüzden imaj, core tariflerinin derleme bağımlılıklarının Debian karşılıklarını da kurar ve `/bin/sh`'yi Pisi'deki gibi bash yapar.

İlk tam çalıştırmanın sonucu: 245 tarifin 206'sı aarch64 paketi üretir, 6'sı `ExcludeArch` ile atlanır. Kalan 33 tarifin hiçbiri tarif hatası değildir; aşama 2'de, Pisi'nin kendi paketleriyle kurulan kökte derlenir:

- core'un kendi ürettiği şeyleri isteyenler: kurulu kernel (`/etc/kernel`, klibc ve kernel modülleri), Python 2 modülleri (dbus, pytz, docutils), elogind.
- Debian ortamından kaynaklananlar: Debian'ın python3'ü modülleri `/usr/local` altına kurar; libtool'u `.la` bağımlılıklarını bağlamaz (gettext); `linux-libc-dev` ile glibc aynı yapıyı iki kez tanımlar (elfutils); GCC 14 C17 varsayar (python); libxml2 ve libgpg-error sürümleri tariflerin istediğinden eskidir.
- Geliştirme makinesinden erişilemeyen kaynaklar (curl.se, docbook.org).

## Aşama 2: Pisi kökü

Aşama 2 dört betikten oluşur. İlki aşama 0 konteynerinde, diğerleri kökten oluşturulan imajın içinde çalışır:

```sh
# 1. Aşama 1 paketlerinden kökü kur ve paketle (aşama 0 konteynerinde)
docker exec pisi-a64 /work/scripts/bootstrap/aarch64/build-stage2-root.sh
docker import --platform linux/arm64 ../stage1/stage2-root.tar pisi-aarch64-stage2:raw

# 2. Kökü çalıştır: core /work, main /main, çıktı /out; catbox için ptrace izni
docker run -d --name pisi-s2 --platform linux/arm64 --cap-add SYS_PTRACE \
    -v "$PWD:/work:ro" -v "$PWD/../../main:/main:ro" -v "$PWD/../stage2:/out" \
    -v pisi-a64-cache:/var/cache/pisi/archives pisi-aarch64-stage2:raw sleep infinity
docker exec pisi-s2 /work/scripts/bootstrap/aarch64/stage2-configure.sh

# 3. Python 3 derleme zinciri: tohum, zincir, tohumun temizlenmesi
docker exec pisi-s2 /work/scripts/bootstrap/aarch64/build-stage2.sh core:system/base/gzip
docker exec pisi-s2 /work/scripts/bootstrap/aarch64/stage2-python-seed.sh
docker exec pisi-s2 /work/scripts/bootstrap/aarch64/build-stage2.sh --passes 3 main:programming/language/python3/python3-installer ...
docker exec pisi-s2 /work/scripts/bootstrap/aarch64/stage2-python-seed.sh --clean
docker exec pisi-s2 /work/scripts/bootstrap/aarch64/stage2-python-seed.sh --check
```

- `build-stage2-root.sh` aşama 1 paketlerini indeksler ve kernel imajı, modüller, firmware ve birbiriyle çakışan initramfs araçları dışında hepsini boş bir köke kurar. Paket betikleri bu adımda çalışmaz. baselayout'un özel dosyalarını (`passwd`, `group`, `ld.so.conf`...) yerleştirir ve kökü `docker import` için tar olarak paketler.
- `stage1-bridge.py`, kökteki programların istediği ama hiçbir paketin sağlamadığı paylaşımlı kütüphaneleri bulur. Aşama 1 programları Debian üzerinde bağlandığı için bazıları yalnızca Debian'da olan kütüphaneleri ister (`libtinfo.so.6`, `libaio.so.1t64`...). Bunlar geçici olarak `/usr/lib/stage1-bridge` dizinine kopyalanır. core yeniden derlendikten sonra köprü silinir ve aynı tarama boş dönmelidir.
- `stage2-configure.sh` kök içinde D-Bus ve COMAR'ı başlatır ve `pisi configure-pending` ile paket betiklerini çalıştırır. Kaynak indirebilmek için önce ca-certificates'in betiğini elle çalıştırır, comar-api'yi de kök içinde derler (Debian'ın Python 2'sinde dbus modülü olmadığı için aşama 1'de derlenemez).
- `build-stage2.sh` verilen tarifleri (`core:<yol>` ya da `main:<yol>`) kök içinde, catbox sandbox'ı açıkken derler. Derlenen her paketi hemen köke kurar; böylece sonraki tarifler köprüye değil, Pisi'nin yeniden derlenmiş kütüphanelerine bağlanır.
- `stage2-python-seed.sh`, Python 3 derleme araçlarının (flit_core, installer, packaging, pyproject_hooks, build, setuptools, wheel) birbirini gerektirdiği döngüyü kırar. Bu araçları tariflerin kendi kaynaklarından derleyip PiSi'siz kurar ve kurduğu dosyaları kaydeder. Zincirin gerçek paketleri bu dosyaların üzerine kurulur. `--clean` hiçbir pakete ait olmayan tohum dosyalarını siler, ardından `--check` boş dönmelidir.

core'un Python 3 tarifleri (python3-setuptools, python3-packaging, meson) main'deki derleme araçlarına dayanır; zincirin tam listesi ve sırası bu araçların `BuildDependencies` ve `RuntimeDependencies` alanlarından hesaplanır (48 tarif). x86-64'teki `pisilinux/chroot` imajında bu araçlar hiçbir pakete ait olmayan dosyalar olarak durur; aarch64'te hepsi paketten gelir.

Ölçülen sonuç: kök 495 paketle kurulur, köprü 23 Debian kütüphanesiyle kapanır, `configure-pending` bütün paketleri yapılandırır. Python zincirinin 48 tarifinin hepsi kök içinde sandbox açıkken derlenir, meson 1.12.1 çalışır ve tohumdan hiçbir sahipsiz dosya kalmaz.

