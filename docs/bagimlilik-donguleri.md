# Bağımlılık Döngüleri ve Derleme Sırası

Core deposundaki paketler birbirine hem derleme hem çalışma zamanı bağımlılığıyla bağlıdır ve bu bağımlılıklar döngüler oluşturur. Bir döngüdeki paketler sıfırdan (bootstrap) derlenirken sırayla değil, aşamalı olarak derlenir: önce döngüyü kıracak biçimde eksik özelliklerle, sonra tam bağımlılıklarla yeniden.

Bu belge döngülerin güncel listesini değil, nasıl üretileceğini ve nasıl yorumlanacağını anlatır. Liste depoya commit edilmez; çünkü her bağımlılık değişikliğinde eskir. (Daha önce kök dizinde duran `circle_and_problems_in_core.txt` ve `needed_build.txt` böyle eskimiş çalıştırma çıktılarıydı; bu belge onların yerini alır.)

## Döngüleri Üretmek

Betik, `pisi` modülüne ihtiyaç duyduğu için chroot içinde ya da Pisi GNU/Linux üzerinde çalışır:

```sh
scripts/circledep-finder pisi-index.xml.xz
```

Çıktı iki bölümden oluşur:

- **Dependencies without a source package:** bağımlılık olarak yazılmış ama bu depoda kaynağı bulunmayan paketler. Bunlar ya `main` deposundadır (core'un `main`'e bağımlı olduğu anlamına gelir) ya da adı yanlış yazılmıştır.
- **Circular dependencies:** karşılaşılan her döngü, döngüyü oluşturan kaynak paket listesiyle.

## Bilinen Döngü Sınıfları

2026-09 tarihli indeks üzerinde alınan sonuç şu sınıflara ayrılır. Son sütun döngüyü kırmak için diğer dağıtımların da kullandığı genel yaklaşımı verir; çiftliğin fiili bootstrap sırası ayrıca belgelenmemiştir.

| Döngü | Neden | Olası bootstrap yaklaşımı |
|-------|-------|---------------------|
| `gcc` ↔ `binutils`, `gmp`, `libmpc`, `isl`, `gettext`, `elfutils`, `zstd`/`ninja` | Derleyici kendi kitaplıklarına ve araçlarına bağımlıdır. | Önce statik, en az özellikli bir gcc (aşama 1); kitaplıklar derlendikten sonra tam gcc. |
| `glibc` ↔ `python3`, `expat`, `libxcrypt`, `mpdecimal` | glibc'nin derlemesi Python 3 ister; Python 3 ise glibc'ye bağlıdır. | Aşama 1 araç zincirinden gelen glibc ile Python 3 derlenir, sonra glibc yeniden. |
| `openssl` ↔ `ca-certificates` ↔ `python3` | Sertifika paketi Python ile üretilir, Python TLS için OpenSSL ister. | Önce sertifikasız OpenSSL ve Python; sertifikalar sonra. |
| `eudev` ↔ `util-linux` | İkisi de birbirinin kitaplıklarını kullanır. | util-linux önce `--without-udev` ile. |
| `glib2` ↔ `gobject-introspection` | Introspection glib2 ile derlenir, glib2 introspection verisi üretmek ister. | glib2 önce introspection'sız. |
| `kernel` → `openssl` → `perl` → `libxcrypt` → `glibc` → `kernel` (başlıklar) | Çekirdek başlıkları glibc için gerekir; çekirdek imzalama OpenSSL ister. | Yalnızca `kernel-headers` aşama 1'de derlenir. |
| `meson` → `python3-setuptools` → `python3-packaging` → `python3` → `openssl` → `xorg-util` → `xorg-proto` → `meson` | Meson tabanlı paketler Python paketleme araçlarına, onlar da Meson'a bağlıdır. | setuptools ve packaging saf Python olarak bootstrap'lanır. |

## Core'un `main`'e Bağımlılıkları

Aynı çalıştırmada core'daki bazı paketlerin `main`'de bulunan kaynaklara bağımlı olduğu görüldü; örneğin `spidermonkey` için `rust`, `llvm` ve `autoconf213`, `python3-setuptools` için birkaç `python3-*` modülü. Bu, core'un tek başına derlenemediği anlamına gelir. Bu bağımlılıklar ya core'a taşınmalı ya da paket `main`'e alınmalıdır; karar paket bazında verilir ve issue ile tartışılır.

## Çiftlikte Derlenmemiş Paketler

Hangi paketlerin çiftlik tarafından henüz derlenmediğini görmek için:

```sh
scripts/find-packages-not-compiled-in-farm \
    https://github.com/pisilinux/core/raw/master/pisi-index.xml.xz \
    https://beta.pisilinux.org/pisi-index.xml.xz
```

Not: depodaki `pisi-index.xml.xz` elle üretilip commit edildiği için tariflerin gerisinde kalabilir. Karşılaştırmadan önce indeksi yeniden üretmek (`pisi index --skip-signing .`) daha doğru sonuç verir.
