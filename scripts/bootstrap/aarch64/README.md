# aarch64 Önyüklemesi

Bu dizin Pisi GNU/Linux'u arm64 (`aarch64`) üzerinde sıfırdan kurmanın ilk adımını içerir. Henüz bir Pisi aarch64 sistemi olmadığı için ilk paketler başka bir arm64 dağıtımının üzerinde, PiSi ile derlenir.

## Aşamalar

| Aşama | Ne yapar | Durum |
|---|---|---|
| 0 | Debian arm64 üzerinde Python 2.7 ve PiSi'yi core tariflerinin kendi kaynak ve yamalarıyla kurar. Bu imajdaki `pisi build` emülasyonsuz aarch64 paketi üretir. | Bu dizin |
| 1 | Aşama 0 ile core'daki tarifleri aarch64 paketlerine dönüştürür (`build-stage1.sh`); sonra bu paketler boş bir köke kurulur. | Derleme betiği hazır |
| 2 | Aşama 1'de oluşan Pisi kökünün içinde core'u kendisiyle yeniden derler; sonuç, x86-64'teki `pisilinux/chroot` imajının aarch64 karşılığıdır. | Sırada |

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
