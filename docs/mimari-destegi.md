# Mimari Desteği

Core deposu x86-64 (`x86_64`) ve arm64 (`aarch64`) için derlenebilecek şekilde düzenlenmiştir. 32 bit desteği, x86-64 üzerinde çoklu kütüphane (multilib, `emul32`) olarak sağlanır; ayrı bir i686 dağıtımı hedeflenmez.

## PiSi tarafı

Mimariye bağlı her bilgi PiSi'nin `pisi/archinfo.py` tablosundan gelir: GNU host triplet'i, varsayılan derleyici bayrakları, kernel `ARCH=` değeri, kernel imajının yolu ve hangi mimaride hangi ek build türünün bulunduğu. Bu değişiklikler core'daki `system/base/pisi` tarifine `files/multiarch/` altındaki yamalarla girer. Ayrıntılar PiSi kaynağındaki `doc/architectures.md` dosyasındadır.

`/etc/pisi/pisi.conf` artık derlenen mimariye göre kurulur (`pisi.conf-x86_64` ya da `pisi.conf-aarch64`).

## Tariflerde kullanılacak yardımcılar

`get.ARCH()` ile dize karşılaştırmak yerine şu yardımcılar kullanılmalıdır; takma adları (`amd64`, `arm64`) tanırlar ve yeni bir mimari eklendiğinde tarif değiştirmek gerekmez:

| Yardımcı | Döndürdüğü |
|---|---|
| `get.isX86_64()`, `get.isAARCH64()`, `get.isI686()` | mimari bu mu |
| `get.isX86()` | x86 ailesinden mi (x86_64 ya da i686) |
| `get.kernelARCH()` | kernel derleme sisteminin `ARCH=` değeri |
| `get.multilibDIR()` | x86_64'te `lib32`, diğerlerinde `None` |
| `get.HOST()` | GNU host triplet'i; derleyici adı `get.HOST() + "-gcc"` |

## 32 bit (emul32)

`<BuildType>emul32</BuildType>` ve `<BuildType>_emul32</BuildType>` paketleri yalnızca x86_64'te derlenir. aarch64'te PiSi bu paketleri kendiliğinden atlar, tariflerde mimari koşulu gerekmez.

## x86'ya özel paketler

Donanımı ya da ikili dosyaları yalnızca x86'da var olan paketler `<ExcludeArch>aarch64</ExcludeArch>` taşır ve nedeni yanındaki yorumda yazılıdır: `module-broadcom-wl`, `module-bbswitch`, `ndiswrapper`, `v86d`, `biosdevname`, `module-virtualbox`. `pisi emerge` bu kaynakları aarch64'te atlar.

## Önyükleme ve kernel

- `grub2`: x86_64'te BIOS (`pc`) ve UEFI (`x86_64-efi`), aarch64'te yalnızca UEFI (`arm64-efi`) derlenir.
- `kernel`: her mimarinin kendi yapılandırması vardır (`files/configs/kernel-<mimari>-config`). `kernel-aarch64-config`, arm64 `defconfig` tabanının üzerine x86 yapılandırmasındaki mimariden bağımsız dağıtım tercihleri ve aarch64 için zorunlu seçenekler (UEFI stub, ACPI, device tree, virtio) eklenerek üretilmiştir; ayrıntılar commit mesajındadır.
- `linux-firmware`: AMD mikrokod erken yükleme imajı yalnızca x86'da üretilir.

## Araç zinciri

- `gcc`: x86_64'te i686 multilib, aarch64'te multilib yok (`--disable-multilib`); `files/pisilinux/aarch64-lib.patch` aarch64 kütüphanelerini de `/usr/lib` altında tutar (x86_64'teki `64.patch`'in karşılığı).
- `glibc`, `libxcrypt`: `-march` mimariye göre seçilir (`x86-64`, `i686`, `armv8-a`).
- `binutils`: EFI (PE32+) hedefi yalnızca x86_64'te eklenir.

## Durum

x86_64'te tüm değişiklikler derlenerek ya da tariflerin ürettiği komutların değişmediği gösterilerek doğrulanmıştır. aarch64 tarafında tariflerin ürettiği komutlar denetlenmiş ve kernel yapılandırması yerel arm64 üzerinde derlenmiştir; aarch64 paketlerinin tamamı ancak aarch64 derleme ortamı (chroot) hazırlandıktan sonra derlenebilir.
