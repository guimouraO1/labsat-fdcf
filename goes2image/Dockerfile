FROM continuumio/miniconda3:24.5.0-0

RUN apt-get update && apt-get install -y cron

COPY environment.yml /tmp/environment.yml
RUN conda env create -f /tmp/environment.yml

RUN echo "conda activate goes" >> ~/.bashrc

COPY --chown=1000:1000 . /home/cpaunicamp/goes2image/

RUN chmod +x /home/cpaunicamp/goes2image/main.py

RUN (crontab -l ; echo "03,13,23,33,43,53 * * * * /opt/conda/envs/goes/bin/python /home/cpaunicamp/goes2image/main.py >> /home/cpaunicamp/goes2image/logs/process_error_fdcf.log 2>&1") | crontab -

CMD ["cron", "-f"]