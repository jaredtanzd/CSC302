FROM python:3.9
ENV DASH_DEBUG_MODE True
ADD main.py .
ADD movie_metadata.csv .
RUN pip install pandas dash 
EXPOSE 8050
CMD ["python", "main.py"]
