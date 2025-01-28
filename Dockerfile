FROM python:3

WORKDIR /app
COPY . .

RUN pip install --no-cache-dir -r requirements.txt

# Default environment variables for Stockholm, Sweden
ENV SOLAR_LATITUDE=59.3293 \
    SOLAR_LONGITUDE=18.0686 \
    SOLAR_COLOR_NIGHT="1,1,10,10" \
    SOLAR_COLOR_MORNING="5,5,40,50" \
    SOLAR_COLOR_NOON="255,255,251,255"

EXPOSE 6060

CMD ["python", "solar.py"]
