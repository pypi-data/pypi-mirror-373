import random


def generate_perm_like_id(prefix="2-"):
    number = random.randint(1000000000, 9999999999)  # 生成 10 位随机数字
    return f"{prefix}{number}"


def generate_unique_perm_like_ids(count):
    unique_ids = set()
    while len(unique_ids) < count:
        unique_ids.add(generate_perm_like_id())
    return list(unique_ids)


if __name__ == "__main__":
    # 调用生成 ID
    # generated_id = generate_perm_like_id()
    # print(generated_id)

    # 生成 5 个唯一的 ID
    unique_ids = generate_unique_perm_like_ids(20)
    for item in unique_ids:
        print(item)
