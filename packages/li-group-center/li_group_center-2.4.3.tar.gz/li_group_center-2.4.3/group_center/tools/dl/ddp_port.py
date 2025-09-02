import sys

from group_center.utils.network.port import check_port


def get_torch_distributed_port() -> int:
    """Get an available port for PyTorch distributed training
    获取用于PyTorch分布式训练的可用端口

    Returns:
        int: An available port number starting from 29500
        从29500开始的可用端口号
    """
    port = 29500

    if sys.platform not in ["linux", "win32", "darwin"]:
        return port

    while not check_port(port):
        port += 1
    return port


def main():
    """Main function to print the available port
    主函数，打印可用端口
    """
    print(get_torch_distributed_port())


if __name__ == "__main__":
    main()
