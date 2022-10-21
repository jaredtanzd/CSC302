FROM python:3.9
ENV DASH_DEBUG_MODE True
COPY . .
RUN pip install pandas dash sklearn statsmodels
EXPOSE 8050
CMD ["python", "src/main.py"]