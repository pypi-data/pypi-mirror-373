from urllib.parse import urlparse


def website_url_standardize(website: str) -> str:
    """
    Standardize website URL.
    """
    # 去掉尾部的 "/"
    website = website.rstrip("/")

    # 如果没有 http:// 或 https://，默认加上 https://
    if not website.startswith(("http://", "https://")):
        website = "https://" + website

    # 解析 URL
    website_parsed = urlparse(website)

    # 获取端口号（如果有）
    port = website_parsed.port

    # 构造标准化 URL，省略默认端口（http:80, https:443）
    if (website_parsed.scheme == "http" and port == 80) or (website_parsed.scheme == "https" and port == 443):
        website_new = f"{website_parsed.scheme}://{website_parsed.hostname}"
    else:
        website_new = f"{website_parsed.scheme}://{website_parsed.hostname}" + (f":{port}" if port else "")

    return website_new


def website_url_compare(website1: str, website2: str) -> bool:
    """
    只比较 hostname 即可。
    :param website1: website url 1
    :param website2: website url 2
    :return: 比较结果
    """
    return urlparse(website1).hostname == urlparse(website2).hostname
