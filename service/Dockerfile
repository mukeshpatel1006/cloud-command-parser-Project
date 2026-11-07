FROM python:3.11-slim
WORKDIR /app
# CPU-only torch (no CUDA libs) keeps the image far below 2 GB. Model weights are NOT in the image.
COPY service/requirements.txt .
RUN grep -v '^torch==' requirements.txt > req-rest.txt \
 && pip install --no-cache-dir torch==2.5.1 --index-url https://download.pytorch.org/whl/cpu \
 && pip install --no-cache-dir -r req-rest.txt
COPY service/app.py service/validation.py service/schema.json /app/
EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
