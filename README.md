[![Telegram](https://img.shields.io/badge/Telegram-Pisi%20GNU%2FLinux-blue)](https://t.me/joinchat/DnOmFNS_KOjzEpnn)
[![Forum](https://img.shields.io/badge/Forum-Pisi%20GNU%2FLinux-orange)](https://pisilinux.org/forum)
[![Website](https://img.shields.io/badge/Website-Pisi%20GNU%2FLinux-green)](https://pisilinux.org/)
# DİKKAT: Geliştiriciler içindir, sisteminize zarar verebilir.
![](https://github.com/PisiLinuxNew/package-manager/blob/master/data/tray-zero.png)

# Pisi GNU/Linux

Pisi GNU/Linux; Pisi tabanlı son Pardus sürümünü temel alan, özgür yazılım topluluğu tarafından geliştirilen, bilgisayar kullanıcılarına kurulum, yapılandırma ve kullanım konusunda kolaylık sağlamaya çalışan, onların temel masaüstü gereksinimlerini karşılamayı amaçlayan, son kullanıcı odaklı bir GNU/Linux dağıtımıdır.

**_Bu depo Pisi GNU/Linux projesinin X bağımlılığı olmadan çalışabilen asgari bileşenlerini içerir._** Masaüstü ortamları, uygulamalar ve diğer her şey [main](https://github.com/pisilinux/main) deposundadır.

## Depo Yapısı

Depo ikili paket içermez; yalnızca PiSi paket yöneticisinin derleme tariflerini barındırır. Tarifler bileşen ağacına göre dizinlenmiştir:

| Dizin | İçerik |
|-------|--------|
| `system/base` | Temel sistem: glibc, bash, coreutils, openssl, pisi, mudur, comar, eudev |
| `system/boot` | Önyükleyiciler: grub2, os-prober |
| `system/devel` | Araç zinciri: gcc, binutils, autotools, cmake, meson |
| `kernel/kernel` | Linux çekirdeği |
| `kernel/drivers` | Ağaç dışı çekirdek modülleri |
| `kernel/tools` | initramfs üreticileri, cpupower |
| `programming/language` | Python 2 ve Python 3 modülleri |
| `programming/library` | Genel amaçlı kitaplıklar |
| `hardware/disk`, `hardware/firmware` | Disk araçları, aygıt yazılımları |
| `office/docbook` | DocBook araç zinciri |
| `desktop/font`, `multimedia/graphics` | freetype, libpng |

Kök dizindeki dosyalar:

- `components.xml`: bu depodaki bileşenlerin adları ve açıklamaları. Her bileşenin dizininde bir `component.xml` bulunur.
- `groups.xml`: paket yöneticisinde görünen grup adları.
- `distribution.xml`: dağıtım kimliği ve artık kullanılmayan (obsolete) paketlerin listesi.
- `pisi-index.xml`, `pisi-index.xml.xz`: tariflerden üretilen kaynak indeksi. Derleme çiftliği ve chroot imajı bu dosyayı GitHub üzerinden okur.

## Paket Anatomisi

Her paket bir dizindir ve şu dosyalardan oluşur:

- `pspec.xml`: kaynak arşivi, sürüm, bağımlılıklar, paketlenecek dosya yolları ve sürüm geçmişi (`<History>`).
- `actions.py`: `pisi.actionsapi` ile yazılmış derleme adımları (`setup`, `build`, `install`).
- `files/`: yamalar ve pakete eklenecek ek dosyalar.
- `translations.xml`: özet ve açıklamaların çevirileri.
- `comar/`: ÇOMAR betikleri (yalnızca gerektiğinde).

## Paketleme Kuralları

1. Ana sürümler dışında **_toolchain_** güncellemesinden kaçınılmalıdır.
1. ```configure``` seçeneklerinde belge oluşturmaya yönelik seçenekler açılmamalı, bağımlılıklar yazılmalıdır.
1. ```configure``` seçeneklerinde pakete yeni bağımlılık getirecek değişiklikler için mutlaka issue açılmalı, tartışılmadan Pull Request istenmemelidir.
1. systemd olmadığı için paketleri yapılandırırken ```--with-systemdsystemunitdir=/lib/systemd/system``` yerine ```--with-systemdsystemunitdir=no``` kullanılmalıdır.
1. Bir paketi yapılandırırken ```--libexecdir=``` kullanılacaksa ```--libexecdir=/usr/lib``` şeklinde kullanılmalıdır.
1. `pspec.xml` ve `actions.py` dosyalarında sekme (Tab) yerine boşluk kullanılmalıdır.
1. Her sürüm yükseltmesi `<History>` altına yeni bir `<Update>` kaydı ile eklenmeli; kayıt tarih, sürüm ve değişikliğin nedenini içermelidir.

## Yerel Derleme

Paketler resmi chroot imajı içinde derlenir. Docker ile:

```sh
docker run --rm -it --platform linux/amd64 -v "$PWD:/work:ro" pisilinux/chroot:latest
```

Kapsayıcı içinde:

```sh
cp -r /work/system/base/which /tmp && cd /tmp/which
pisi bi -y pspec.xml
```

Notlar:

- `pisi bi` derleme bağımlılıklarını kendisi kurar. Bağımlılıkları atlamak için `--ignore-dependency`, sürüm geçmişi denetimini atlamak için `--ignore-safety` kullanılabilir.
- PiSi'nin derleme sandbox'ı `ptrace` kullanır. Emülasyon altında (örneğin arm64 bir makinede) sandbox çalışmaz; bu durumda `--ignore-sandbox` eklenmelidir.
- Üretilen `.pisi` dosyası tarif dizinine yazılır.

## Doğrulama

Bir PR göndermeden önce en azından şunlar yapılmalıdır:

```sh
xmllint --noout system/base/which/pspec.xml     # XML geçerliliği
python -m py_compile system/base/which/actions.py   # Python 2 söz dizimi
```

Ardından paket chroot içinde derlenmeli ve derleme günlüğü hatasız bitmelidir.

## Katkı

Pisi GNU/Linux projesinin geliştirilmesine yardım etmek istiyorsanız;

* Öncelikle kendi GitHub hesabınıza projeyi fork'layın,
* Her değişiklik için ayrı bir dal açın,
* Yaptığınız değişiklikleri Pull Request ile gönderin. PR açıklamasında neyi, neden değiştirdiğinizi ve nasıl doğruladığınızı yazın.
