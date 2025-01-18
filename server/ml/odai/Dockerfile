# NVIDIAのCUDA 12.4.1ベースのイメージを使用
ARG CUDA_IMAGE="12.4.1-runtime-ubuntu22.04"
FROM nvidia/cuda:${CUDA_IMAGE}

# タイムゾーンの設定
ENV TZ=Asia/Tokyo
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# ディレクトリを設定
WORKDIR /app

# 必要なパッケージのインストール
RUN apt-get update && apt-get upgrade -y \
    && apt-get install -y git build-essential \
    python3 python3-pip gcc wget \
    ocl-icd-opencl-dev opencl-headers clinfo \
    libclblast-dev libopenblas-dev \
    && mkdir -p /etc/OpenCL/vendors && echo "libnvidia-opencl.so.1" > /etc/OpenCL/vendors/nvidia.icd \
    && rm -rf /var/lib/apt/lists/*

# 環境変数の設定 (CUDA用の設定)
ENV CUDA_DOCKER_ARCH=all
ENV GGML_CUDA=1

# HOSTをCloud Runに適した設定に変更, Cloud Runでは8080ポートがデフォルト
ENV HOST 0.0.0.0
ENV PORT 8080

# 必要なコードをコンテナにコピー
COPY . .

# 依存関係をインストール
RUN python3 -m pip install --upgrade pip \
    && pip install pytest cmake scikit-build setuptools \
    && pip install fastapi uvicorn sse-starlette pydantic-settings starlette-context

# llama-cpp-pythonをCUDA対応でアーキテクチャ指定してインストール
RUN CMAKE_ARGS="-DGGML_CUDA=on -DCMAKE_CUDA_ARCHITECTURES=86" pip install llama-cpp-python

# requirements.txtでllama-cpp-pythonと関係のないパッケージをインストール
RUN python3 -m pip install -r requirements.txt

# 必要なポートを公開
EXPOSE 8080

# アプリケーションのエントリーポイントを設定
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]
