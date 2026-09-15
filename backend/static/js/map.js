// Google Maps initialisation for Support Centers and Hospitals pages

function initSupportCentersMap() {
  const mapElement = document.getElementById("supportCentersMap");
  if (!mapElement) return;

  const center = { lat: 12.9716, lng: 77.5946 }; // Example: Bengaluru

  const map = new google.maps.Map(mapElement, {
    zoom: 12,
    center: center,
  });

  // Example markers (you can adjust later based on real data)
  const markers = [
    { position: { lat: 12.98, lng: 77.60 }, title: "Support Center 1" },
    { position: { lat: 12.96, lng: 77.58 }, title: "Support Center 2" },
  ];

  markers.forEach((m) => {
    new google.maps.Marker({
      position: m.position,
      map: map,
      title: m.title,
    });
  });
}

function initHospitalsMap() {
  const mapElement = document.getElementById("hospitalsMap");
  if (!mapElement) return;

  const center = { lat: 12.9716, lng: 77.5946 };

  const map = new google.maps.Map(mapElement, {
    zoom: 12,
    center: center,
  });

  const markers = [
    { position: { lat: 12.975, lng: 77.59 }, title: "Hospital 1" },
    { position: { lat: 12.965, lng: 77.605 }, title: "Hospital 2" },
  ];

  markers.forEach((m) => {
    new google.maps.Marker({
      position: m.position,
      map: map,
      title: m.title,
    });
  });
}
