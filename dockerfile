FROM python:3.8.5-alpine3.11

# ==============================================================================
# 타임존 설정
RUN apk add tzdata && \
    cp /usr/share/zoneinfo/Asia/Seoul /etc/localtime && \
    echo "Asia/Seoul" > /etc/timezone

ENV PYTHONUNBUFFERED=0

# ==============================================================================
# 파일 복사
RUN mkdir -p /src/Library_management
ADD Library_management /src/Library_management
ADD setup.py /src
WORKDIR /src

# ==============================================================================
# 설치
RUN pip install -r Library_management/requirements.txt

# ==============================================================================
# 설치파일 정리
WORKDIR /root
RUN rm -rf /src

EXPOSE 5000
VOLUME ["/root"]
ENTRYPOINT ["python" , "-m", "Library_management"]
