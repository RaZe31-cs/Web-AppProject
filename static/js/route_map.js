let coordinates = [];

ymaps.ready(init);


function init () {
    var myMap = new ymaps.Map('routeMap', {
        center: center_points,
        zoom: 15,
        controls: ['zoomControl']
    });

    myMap.behaviors.enable("scrollZoom");

    var polyline = new ymaps.Polyline([], {}, {
	    strokeColor: '#463830',
        strokeWidth: 5
    });

	myMap.geoObjects.add(polyline);
	polyline.editor.startEditing();
	polyline.editor.startDrawing();


var stopEditButton = document.getElementById('stopEditPolyline');

stopEditButton.addEventListener('click',
    function () {
        polyline.editor.stopEditing();
    });

var newButton = document.getElementById('newPolyline');

newButton.addEventListener('click',
    function() {
                myMap.destroy();
                init()
            });

var generateButton = document.getElementById('generate');

generateButton.addEventListener('click',
    function() {
    myMap.destroy();
    init2();
});

var saveEditButton = document.getElementById('save');

saveEditButton.addEventListener('click',
    function () {
    returnGeometry({coords: polyline.geometry.getCoordinates(), type: -1});
    });
}


function init2() {
    var myMap = new ymaps.Map('routeMap', {
        center: center_points,
        zoom: 15,
        controls: ['zoomControl']
    });
    let index = -1;
    var geometry = [];
    myMap.behaviors.enable("scrollZoom");
    alert("Укажите на карте точки начала и окончания маршрута");
    myMap.events.add('click', function (event) {
                var coords = event.get('coords');
                coordinates.push([coords[0], coords[1]]);
                myPlacemark = new ymaps.Placemark([coords[0], coords[1]], {
                }, {
                    preset: 'twirl#brownIcon'
                });
                myMap.geoObjects.add(myPlacemark)

                if (coordinates.length === 2) {
                    fetch('/route/generate', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({city_iata: city_iata, start: coordinates[0], end: coordinates[1]})
                    })
                    .then(response => response.json())
                    .then(data => {
                        geometry = data['coords']
                        properties = {},
                        options = {
                            strokeColor: '#463830',
                            strokeWidth: 5
                        },
                        polyline = new ymaps.Polyline(geometry, properties, options);

                        myMap.geoObjects.add(polyline);
                        coordinates = [];
                        index = data['index']
                    });
                }
            });


var stopEditButton = document.getElementById('stopEditPolyline');

stopEditButton.addEventListener('click',
    function () {
        myMap.destroy();
        init();
    });

var newButton = document.getElementById('newPolyline');

newButton.addEventListener('click',
    function() {
                myMap.destroy();
                init()
            });

var generateButton = document.getElementById('generate');

generateButton.addEventListener('click',
    function() {
        myMap.destroy();
        init2();
});

var saveEditButton = document.getElementById('save');

saveEditButton.addEventListener('click',
    function () {
    returnGeometry({coords: geometry, type: 1})
    coordinates = [];
    });
}


function returnGeometry (data) {
    if (data['type'] == -1) {
    var data_return = {route: jsoncoords(data['coords']), city_iata: city_iata, index: index, type: 'new'};
        fetch('/route/' + city, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(data_return),
        })
        .then(response => response.json())
        .then(data => {
        });
    function jsoncoords(coords) {
        var res = [];
        if ($.isArray(coords)) {
            for (var i = 0, l = coords.length; i < l; i++) {
                res.push(coords[i]);
            }
        }
        else if (typeof coords == 'number') {
            res = coords.toPrecision(6);
        }
        else if (coords.toString) {
            res = coords.toString();
        }
        return res
    }}
    else {
        fetch('/route/' + city, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({route: data['coords'], city_iata: city_iata, index: index, type: 'created'})
                    })
                    .then(response => response.json())
                    .then(data => {
                    });
    }
}
