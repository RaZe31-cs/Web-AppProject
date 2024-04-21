window.map = null


async function initMap(lon, lat, all_points) {
    all_points = all_points.split(';')

    await ymaps3.ready;

    const {YMap, YMapDefaultSchemeLayer, YMapDefaultFeaturesLayer} = ymaps3;

    const {YMapDefaultMarker} = await ymaps3.import('@yandex/ymaps3-markers@0.0.1');

    window.map = new YMap(
        document.getElementById('map'),
        {
            location: {
                center: [Number(lat), Number(lon)],
                zoom: 10
            }
        }
    );

    window.map.addChild(new YMapDefaultSchemeLayer());
    window.map.addChild(new YMapDefaultFeaturesLayer());
    for (let i = 0; i < all_points.length; i++) {
        const [lon, lat] = all_points[i].split(',')
        const marker = new YMapDefaultMarker({
            coordinates: [Number(lat), Number(lon)]
        });
        window.map.addChild(marker);
        };
        
}


async function deleteMap() {
    alert('Карта удалена')
    window.map.destroy();
}


async function changeCenter(el) {
    const {YMapMarker} = ymaps3;

    var parent = el.parentNode.parentNode;
    // Получаем родительский div
    var h6Element = parent.querySelector('h6');   
    var h4Element_title = parent.getElementsByTagName("h4");
    //Находим в нем h6
    var longitude = h6Element.getAttribute('data-coord1');
    var latitude = h6Element.getAttribute('data-coord2');
    //Записываем атрибуты
    window.map.setLocation({
        center: [Number(longitude), Number(latitude)],
        zoom: 17
      })
    const content = document.createElement('section');
}


async function changeCenter_by_coords(coords, title) {
    alert(coords)
    window.map.setLocation({
        center: coords,
        zoom: 5
      })
    const content = document.createElement('section');
}


async function save_trip(coords, title) {

}


async function request_post(lon, lat, title) {
    alert('Запрос отправлен')
    alert(lon + ' ' + lat + ' ' + title)
    fetch('/save_trip', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(
            {
                'lon': lon,
                'lat': lat,
                'title': title
            }
        )
    })
}