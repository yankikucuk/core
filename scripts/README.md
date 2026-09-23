# Yardımcı Betikler

Bu dizindeki betikler depo bakımında kullanılır; paket derlemesinin parçası değildir.

| Betik | Ne yapar | Çalıştığı Python |
|-------|----------|------------------|
| `circledep-finder` | Kaynak indeksindeki döngüsel bağımlılıkları ve kaynağı bulunamayan bağımlılıkları raporlar. | 2.7 (`pisi` ve `piksemel` modülleri yalnızca Python 2 için var) |
| `find-packages-not-compiled-in-farm` | Depo indeksini çiftliğin ikili indeksiyle karşılaştırır; hiç derlenmemiş ya da sürümü yükseltilmiş ama yeniden derlenmemiş paketleri listeler. | 2.7 ve 3 |
| `validate-specs` | Her `pspec.xml` dosyasını PiSi'nin kendi ayrıştırıcısıyla okur ve reddedilenleri nedeniyle listeler; CI iş akışı bunu kullanır. | 2.7 (`pisi` modülü) |
| `history_reset.py` | Yeni bir depo nesli başlatırken tüm `pspec.xml` dosyalarının `<History>` bloğunu tek kayda indirir; özgün dosyaları yedekler. | 2.7 ve 3 |

Örnekler:

```sh
# Döngüsel bağımlılıklar (chroot içinde ya da Pisi GNU/Linux üzerinde)
scripts/circledep-finder pisi-index.xml.xz

# Çiftlik hangi paketleri derlememiş?
scripts/find-packages-not-compiled-in-farm \
    https://github.com/pisilinux/core/raw/master/pisi-index.xml.xz \
    https://beta.pisilinux.org/pisi-index.xml.xz

# Tüm tarifler PiSi tarafından okunabiliyor mu? (chroot içinde)
scripts/validate-specs .

# Sürüm geçmişini sıfırla (önce ../backup altına yedekler)
scripts/history_reset.py --root . --backup-dir ../backup
```

Her betik `--help` ile kullanımını açıklar.
