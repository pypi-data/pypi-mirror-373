# Python I2C Driver for Sensirion STC42

This repository contains the Python driver to communicate with a Sensirion STC42A sensor over I2C.

<img src="https://raw.githubusercontent.com/Sensirion/python-i2c-stc42/master/images/product-image.png"
    width="300px" alt="STC42 picture">


Click [here](https://sensirion.com/products/catalog/STC42A) to learn more about the Sensirion STC42A sensor.


The STC42A is a sensor for measuring hydrogen in air.



The default I²C address of [STC42A](https://sensirion.com/products/catalog/STC42A) is **0x29**.
Additionally supported I²C addresses are 0x2A, 0x2B.


## Connect the sensor

You can connect your sensor over a [SEK-SensorBridge](https://developer.sensirion.com/product-support/sek-sensorbridge/).
For special setups you find the sensor pinout in the section below.

<details><summary>Sensor pinout</summary>
<p>
<img src="https://raw.githubusercontent.com/Sensirion/python-i2c-stc42/master/images/product-pinout.jpg"
     width="300px" alt="sensor wiring picture">

| *Pin* | *Cable Color* | *Name* | *Description*  | *Comments* |
|-------|---------------|:------:|----------------|------------|
| 1 | black | GND | Ground |
| 2 | red | VDD | Supply Voltage | 3.15V to 3.45V
| 3 | blue | SDA | I2C: Serial data input / output |
| 4 | yellow | SCL | I2C: Serial clock input |


</p>
</details>


## Documentation & Quickstart

See the [documentation page](https://sensirion.github.io/python-i2c-stc42) for an API description and a
[quickstart](https://sensirion.github.io/python-i2c-stc42/execute-measurements.html) example.


## Contributing

### Check coding style

The coding style can be checked with [`flake8`](http://flake8.pycqa.org/):

```bash
pip install -e .[test]  # Install requirements
flake8                  # Run style check
```

In addition, we check the formatting of files with
[`editorconfig-checker`](https://editorconfig-checker.github.io/):

```bash
pip install editorconfig-checker==2.0.3   # Install requirements
editorconfig-checker                      # Run check
```

## License

See [LICENSE](LICENSE).