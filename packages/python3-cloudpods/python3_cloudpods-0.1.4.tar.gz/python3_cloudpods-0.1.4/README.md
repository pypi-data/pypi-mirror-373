# python3-cloudpods 文档

# 一、python3-cloudpods 文档
## 1.1 python3-cloudpods 安装
```bash
pip install python3-cloudpods
```
## 1.2 python3-cloudpods 使用
```python
from cloudpods import CloudPods

# 初始化
cloudpods = CloudPods("https://10.30.18.1:30500/v3","admin","xxx")

# 然后即可调用cloudpods的api了
# 根据虚拟机的 id 获取虚拟机的 ip 地址
server_ip = cloudpods.get_server_ip("e3b76ec7-c4f9-4065-8ce2-9d833b51368c")

# 获取物理机的信息列表
rs=cloudpods.get_baremetal_hosts()
print(len(rs["hosts"]))

# 获取裸金属列表
rs=cloudpods.get_baremetal_servers()
print(len(rs["servers"]))

# 根据虚拟机的 id 删除虚拟机
rs=cloudpods.delete_server("8c925c8e-752f-4358-8c3e-a80847732d91")

# 判断物理机是否包含裸金属
rs=cloudpods.host_has_baremetal_server("fa09da4e-b6d7-4a07-855d-d690abea66a9")

# 获取物理机的规格信息
rs=cloudpods.get_host_spec("fa09da4e-b6d7-4a07-855d-d690abea66a9")

# 创建裸金属
rs=cloudpods.create_server_by_guest_image("8572ed8a-6ffe-451a-80ac-c04da95e777f","1fdfbc15-e319-4f59-8e2b-cc45bc3517cb",
                                           "x86_64",20480,[20],["265005a2-b3a4-42e3-8154-471bdd694487"],"demo2",hypervisor="baremetal",bios="UEFI",
                                           cpu=256,mem=2097152
                                           )
```