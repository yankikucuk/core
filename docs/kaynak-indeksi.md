# Kaynak İndeksi

`pisi-index.xml.xz`, depodaki tüm `pspec.xml` dosyalarından üretilen kaynak indeksidir. Chroot imajı ve derleme çiftliği paket listesini bu dosyadan okur; `pisi bi`/`pisi emerge` hangi paketin hangi sürümde olduğunu buradan öğrenir.

## Nerede yayınlanır

İndeks depoya commit edilmez. `master` dalına tarif değişikliği girdiğinde `.github/workflows/indeks.yml` iş akışı chroot imajı içinde `pisi index` çalıştırır ve dosyaları sabit `index` etiketli GitHub sürümüne yükler:

```
https://github.com/pisilinux/core/releases/download/index/pisi-index.xml.xz
https://github.com/pisilinux/core/releases/download/index/pisi-index.xml.xz.sha1sum
```

`index` etiketi sürüm numarası taşımaz; her çalışmada dosyaların üstüne yazılır. Adres sabit olduğu için `pisi ar` ile bir kez eklenir:

```sh
pisi ar core https://github.com/pisilinux/core/releases/download/index/pisi-index.xml.xz
```

## Neden depoda değil

Daha önce indeks elle üretilip depoya commit ediliyordu. Bu iki soruna yol açıyordu: üretilmiş 19 MB'lık bir dosya her sürüm yükseltmesinde git geçmişini büyütüyordu ve indeks tariflerin gerisinde kalıyordu (2026-04'te üretilen indeks, Eylül 2026'da 241 paketin 60'ını eski sürümde gösteriyordu). İş akışı her değişiklikte üretim yaptığı için indeks artık tariflerle aynı commit'i yansıtır.

## Yerelde üretmek

Bir chroot ya da Pisi GNU/Linux üzerinde:

```sh
pisi index --skip-signing . -o pisi-index.xml
xz -9 -k pisi-index.xml
```

Not: `pisi index` tarifleri bir işlem havuzuyla okur; Rosetta emülasyonu altında (arm64 Mac) havuz kilitlenir. Tariflerin geçerliliğini denetlemek için `scripts/validate-specs` yeterlidir, indeks üretimi için gerçek bir x86-64 makine gerekir.

## Geçiş

Chroot imajı (`pisilinux/chroot`) ve çiftlik yapılandırması hâlâ `https://github.com/pisilinux/core/raw/master/pisi-index.xml.xz` adresini kullanıyor. Bu iş akışı devreye girdikten sonra o adres boş dönecek; `pisi-chroot-build` ve çiftlik ayarlarındaki depo adresi yukarıdaki sürüm adresiyle değiştirilmelidir. main deposu için aynı düzen ayrı bir PR ile kurulur.
