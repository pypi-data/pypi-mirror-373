def merge_dicts(dict1, dict2):
    """合并两个字典，支持嵌套字典的合并"""
    merged = dict1.copy()  # 复制第一个字典
    for key, value in dict2.items():
        if key not in merged:
            merged[key] = value  # 直接添加新键值对
        else:
            # 如果值是字典，则递归合并
            if isinstance(merged[key], dict) and isinstance(value, dict):
                merged[key] = merge_dicts(merged[key], value)
            else:
                # 否则，选择第二个字典的值（可以根据需求调整）
                merged[key] = value
    return merged
