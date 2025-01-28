# Solar Elevation

Silly little hack which calculates the color of an RGBW strip based 
on the elevation of the sun.

Goal is to simulate (if poorly) the light which the sun would shine
into the skylight of a building.

This is far from an exact science and more something which looks ok
for me.

## Usage

```
docker run -d --name solar-elevation -p 6060:6060 solar-elevation
```

You can also set the latitude, longitude, and colors by setting the
environment variables.

```
docker run -d --name solar-elevation -p 6060:6060 -e SOLAR_LATITUDE=59.3293 -e SOLAR_LONGITUDE=18.0686 -e SOLAR_COLOR_NIGHT="1,1,10,10" -e SOLAR_COLOR_MORNING="5,5,40,50" -e SOLAR_COLOR_NOON="255,255,251,255" solar-elevation
```

Once this is running, you can get the current color of the strip by
calling the `/color` endpoint.

```
curl http://localhost:6060/color
```

which returns something like this:

```
{"color": [255, 255, 251, 255]}
```

## Home Assistant

You can use this in Home Assistant by adding the following to your configuration:

```
  - platform: rest
    name: "Sun color"
    resource: http://localhost:6060/rgbw
    value_template: "{{ value_json.rgbw }}"
    scan_interval: 60
```

The following automation will change the color of the strip based on the
sun elevation.

```
alias: Skylight
description: ""
mode: single
triggers:
  - entity_id:
      - sensor.sun_color
    trigger: state
actions:
  - data_template:
      entity_id: light.entryway_rgbw
      rgbw_color: "{{ trigger.to_state.state | from_json }}"
    action: light.turn_on
```
