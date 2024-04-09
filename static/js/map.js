window.map = null

initMap()


async function initMap() {
    await ymaps3.ready;

    const {YMap, YMapDefaultSchemeLayer, YMapDefaultFeaturesLayer} = ymaps3;

    window.map = new YMap(
        document.getElementById('map'),
        {
            location: {
                center: [37.588144, 55.733842],
                zoom: 2
            }
        }
    );
    window.map.addChild(new YMapDefaultSchemeLayer());

    window.map.addChild(new YMapDefaultFeaturesLayer());


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
    //Находим в нем h6
    var longitude = h6Element.getAttribute('data-coord1');
    var latitude = h6Element.getAttribute('data-coord2');
    //Записываем атрибуты
    alert(longitude + latitude);  
    window.map.setLocation({
        center: [Number(longitude), Number(latitude)],
        zoom: 17
      })

    const content = document.createElement('section');
    
    const marker = new YMapMarker(
    {
        coordinates: [Number(longitude), Number(latitude)],
        draggable: true
    }
    );
    
    window.map.addChild(marker);
      

}