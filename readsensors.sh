#[[ -s /home/pi/results.csv ]] || echo "Date,Temperature in degree celcius,Humidity in percent,Lux,Soil moisture" >> /home/pi/results.csv
python /home/pi/readsensors.py >> /home/pi/results.csv
