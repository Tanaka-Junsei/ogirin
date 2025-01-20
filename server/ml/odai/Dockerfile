# NVIDIAのCUDA 12.4.1ベースのイメージではなく、通常のUbuntuベースイメージを使用
FROM ubuntu:22.04

# タイムゾーンの設定
ENV TZ=Asia/Tokyo
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# 必要なパッケージのインストール
RUN apt-get update && apt-get upgrade -y \
    && apt-get install -y git build-essential \
    python3 python3-pip gcc wget \
    && rm -rf /var/lib/apt/lists/*

# 作業ディレクトリの設定
WORKDIR /app

# 必要なコードをコンテナにコピー
COPY . .

# 必要なPythonライブラリをインストール
RUN python3 -m pip install --upgrade pip \
    && pip install -r requirements.txt

# llama-cpp-pythonをCPUモードでインストール
RUN CMAKE_ARGS="-DGGML_CUDA=off" pip install llama-cpp-python

# 必要なポートを公開
EXPOSE 8080

# アプリケーションのエントリーポイントを設定
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]
