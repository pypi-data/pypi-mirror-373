import os


def save_to_excel(df, output_file):
    """
    将处理后的DataFrame保存为新的Excel文件
    :param df: 处理后的DataFrame
    :param output_file: 保存的Excel文件路径
    """
    # 获取上级目录
    directory = os.path.dirname(output_file)
    # 如果上级目录不存在，则创建
    if not os.path.exists(directory):
        os.makedirs(directory)

    # 保存 DataFrame 到 Excel
    df.to_excel(output_file, index=False)


def process_and_save_to_excel(df, output_file, index_column, keep='first'):
    """
    处理DataFrame，去除重复记录，并将结果保存为新的Excel文件
    :param df: 输入的DataFrame
    :param output_file: 输出Excel文件的名称
    :param index_column: 用于去重的列名（如'身份证号'）
    :param keep: 'first' 保留第一条记录，'last' 保留最后一条记录
    """
    # 去除重复记录
    df_processed = df.drop_duplicates(subset=index_column, keep=keep)

    # 按原始顺序排序
    df_processed = df_processed.sort_index()

    # 获取上级目录
    directory = os.path.dirname(output_file)
    # 如果上级目录不存在，则创建
    if not os.path.exists(directory):
        os.makedirs(directory)

    # 保存到Excel
    df_processed.to_excel(output_file, index=False)

    print(f"处理完成。结果已写入 {output_file}")

    # 返回处理后的DataFrame
    return df_processed