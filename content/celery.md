Title: Python Celery
Date: 2014-01-10 12:40
slug: python-celery

Sunucu tarafında geliştirme yaparken bazı durumlarda asenkron çalışan process'lere ihtiyaç duyarız. Bu asenkron 
process'leri istemciye anlık cevap verilmesi gerekmeyen veya peryodik olarak çalışması gereken işlemleri yapmak için kullanırız.

Örneğin kullanıcıların sisteme yüklediği resimleri çeşitli boyutlarda işleyip, kayıt altına almamız gerektiğini varsayalım. 
Böylesine kullanıcıya anlık cevap gerektirmeyen bir işlemi, senkron bir şekilde geliştirirsek hem işlem uzun 
süreceğinden sunucunun cevap verme süresi artıcak, hem de eşzamanlı istekler artıkça sunucunun
kaynak tüketimi artıcaktır.

Bu gibi durumları aşmak için **"Background Tasks"** denilen dağıtık olarak çalıştırabileceğimiz sistemler kullanılıyor. Bu
sistemlerden biride [python-celery](http://www.celeryproject.org/){: target=_blank}. 


##Peki Nasıl Çalışıyor ?  

Sistemin ekosistemi 4 farklı bölümden oluşuyor. 
 
* **Publisher** : İstemci tarafından ilgili işlemin çalışması için broker'a mesaj gönderen fonksiyonlardır.
* **Broker** : İstemcinin istediği işlemi ilgili worker'lara yönlendiren ve bunları belirli 
bir sıraya göre yapan kuyruk sistemi. (bkz: [AMQP](http://en.wikipedia.org/wiki/Advanced_Message_Queuing_Protocol){: target=_blank})
* **Worker** : Broker'dan gelen mesaja göre ilgili task'ları çalıştıran ve dağıtık çalışabilen sistemler. 
* **Result Store** : Task çalışıp process bittikten sonra task'ın sonucunu kayıt altına aldığımız veritabanı sistemleri. 

![](/theme/images/celery_schema.png){: class=full-width}


##Kurulum


ilk olarak **Broker**'dan başlayalım. Broker olarak AMQP protokolü üzerinden çalışan [rabbitMQ](rabbitmq.com{: target=_blank}) 
mesaj kuyruğu(message queue) sistemini kuruyoruz. 

    apt-get install rabbitmq-server

**rabbitMQ**'yu kurduktan sonra celery ile birlikte kullanmak için aşağıdaki komutlarla kullanıcı ayarlarını ve virtual host'u tanımlayabilirsiniz.

    rabbitmqctl add_user celeryuser celery
    rabbitmqctl add_vhost celeryvhost
    rabbitmqctl set_permissions -p celeryvhost celeryuser ".*" ".*" ".*"
    service rabbitmq-server restart
 
 
**Worker** olarak sizinde tahmin edeceğiniz üzere [celery](http://www.celeryproject.org/){: target=_blank} kullanacağız. 
    
    pip install celery
    
Son olarak **Result Store** bölümü için bir veritabanı kullanmamız gerekiyor. Result store celery de default olarak kapalı geliyor. 
Config dosyasında gerekli bilgileri düzenlediğinizde aktif oluyor. Result store bölümü yukarıda bahsetiğim gibi bir task'ın beklenen 
şekilde çalıştığını veya çalışmadıysa ne hata verdi gibi bilgileri kayıt altına alıp [monitoring](http://en.wikipedia.org/wiki/Application_performance_management){: target=_blank} 
için kullandığımız bir bölüm. Bu tarz sistem tarafından üretilen log verileri, herhangi bir veriyle ilişkisi olmayacağından 
ve çok fazla veri akışı olduğundan yazma hızı yüksek, ilişkisel olmayan bir veritabanı kullanmamız daha iyi olucaktır. 

Ben genelde result store için  [redis](http://redis.io/){: target=_blank}'i tercih ediyorum. Celery'le birlikte redis kullanıcaksanız. 
Redis'in yanında birde redis python client'ını kurmanız gerekiyor.
 
     apt-get install redis-server
     
     pip install redis
     
##Örnek Uygulama

Yukarıda bahsettiğim resim boyutlandırma örneğini uygulama olarak yapalım. Senaryomuz bize gelen tüm resimleri farklı boyutlarda 
sınıflandırıp bu resimleri farklı klasörlerde kayıt altına almak olsun.
 
Önce celery config dosyasını oluşturalım.

    # BROKER_URL için rabbitMQ tanımladığımız bilgileri giriyoruz. 
    
    # amqp://<kullanıcı_adi>:<şifre>@localhost:5672/<virtual_host>
    BROKER_URL = 'amqp://celeryuser:celery@localhost:5672/celeryvhost'
    
    # Celery result backend'i redis'e yönlendiriyoruz.
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
    
    
    # Son olarak çalıştırılıcak task'ların bulunduğu, dosyaların path'lerini belirtiyoruz.
    CELERY_IMPORTS = ('tasks', )

Celery'nin doğru çalıştığını görmek için aşağıdaki komutla celery worker'ımızı çalıştıralım. 
 
    celery worker --loglevel=INFO
    
    
![](/theme/images/celery_run.jpg){: class=full-width}
  
Eğer celery düzgün çalışıyorsa, karşınıza yukarıdaki gibi bir ekran gelicektir. Bu ekranda belirttiğim yerleri gelicek olursak.

[Concurrency](http://celery.readthedocs.org/en/latest/userguide/workers.html#concurrency){: target=_blank} (eşzamanlı) 
bilgisayar bilimlerinde çok kullanılan bir terim. Kısaca tanımlamak gerekirse bir işlemin farklı thread'lerde eş zamanlı 
çalıştırılması durumudur. İşte celery'deki concurrency sayısı aynı anda çalıştırılabilecek eşzamanlı işlem sayısını gösterir.
Geliştirdiğiniz sistemdeki ihtiyaça göre concurrency artırabilir veya azaltabilirsiniz. 
   
Task yazan bölüm celery worker'a "--loglevel=INFO" parametresi geçtiğimiz için geldi. Bu kısımda celery'e 
register olan task'ların listesini görebilirsiniz.    
  
Celery artık çalıştığına göre, artık geliştirme yapmaya başlayabiliriz. İlk önce çalıştıracağımız task'la başlayalım. 

    import os
    import Image
    
    from celery.task import task
    from constants import THUMBNAIL_SIZES, THUMBNAILS_DIRECTORY
    
    # Bir fonksiyonu celery worker üzerinden çalıştırmak istiyorsanız. 
    
    # Celery task decorator'unu başına eklemeniz gerekiyor.
    
    # Fonksiyonumuz @task decoratoru üzerinden celery'e register etmiş oluyoruz.
    
    @task(name="thumbnail_generater")
    def thumbnail_generater(image_path, image_name):
        for thumbnail_size in THUMBNAIL_SIZES:
            thumbnail_folder_name = "%sx%s/" % thumbnail_size
            thumbnail_directory = THUMBNAILS_DIRECTORY + thumbnail_folder_name
    
            try:
                os.makedirs(thumbnail_directory)
            except OSError:
                pass
    
            thumbnail_data = {
                "image_name": os.path.splitext(image_name)[0],
                "width": thumbnail_size[0],
                "height": thumbnail_size[1]
            }
            thumbnail_name = "%(image_name)s_%(width)sx%(height)s.jpg" % thumbnail_data
            thumbnail_path = thumbnail_directory + thumbnail_name
    
            image = Image.open(image_path)
            image.thumbnail(thumbnail_size)
            image.save(thumbnail_path, "JPEG")

Örnek olarak yazdığım task'ın yaptığı işlem, dizin adresi ve ismi parametre olarak gelen resim dosyasını, belirli 
ölçeklerde işleyip belirtilen bir klasörde kayıt altına alıyor.
   
Son olarak brokerdan task'ın çalışmasını isteyecek publisher'ı yazalım.

    import os
    from tasks import thumbnail_generater
    from constants import IMAGE_DIRECTORY
    
    def generate_thumbnails():
        images = os.listdir(IMAGE_DIRECTORY)
        for image_name in images:
            image_path = IMAGE_DIRECTORY + image_name
            thumbnail_generater.delay(image_path, image_name)

Publisher'ı çalıştıracağımız zaman celery'nin çalışır durumda olması gerekiyor. 

Burada "thumbnail_generater" task'ına çalışması için gerekli parametreleri geçerken, normal fonksiyon gibi 
"thumbnail_generater(image_path, image_name)" şeklinde çağırmadık. Task fonksiyonumuzun başına "@task" 
decorator'u eklediğimiz için fonksiyona "delay" isminde yeni bir attribute/komut eklendi. Delay üzerinden celery broker'a 
işlemin background task olarak çalışmasını istiyor. Eğer normal olarak çağırırsanız işlem normal python process olarak çalışır.

 
Umarım konuyu iyi anlatabilmişimdir. İncelemek isterseniz yazdığım örnek uygulamanın koduna [github](http://www.github.com/erdemozkol/){: target=_blank}
sayfam üzerinden ulaşabilirsiniz. Bir sonraki blog yazımda görüşmek üzere.


