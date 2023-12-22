## 测试 Triton 部署
- 编译后的so文件也可以使用
```shell
docker run --runtime=nvidia --shm-size=1g --ulimit memlock=-1 -p 8000:8000 -p 8001:8001 -p 8002:8002 --ulimit stack=67108864 -ti nvcr.io/nvidia/tritonserver:23.11-py3
docker exec -it fbc5c3a35ffd bash
git clone https://github.com/triton-inference-server/python_backend -b r23.11
cd python_backend
docker cp ai_tools fbc5c3a35ffd:/opt/tritonserver/python_backend/models
tritonserver --model-repository `pwd`/models
```


