import os
from tkinter import Tk, messagebox, filedialog
import tkinter as tk

def showFileDialog(parent_form):
    file_name = filedialog.askopenfilename(
        parent=parent_form,
        title="选择文件",
        filetypes=[("Excel Files", "*.xlsx")]
    )
    return file_name


def showMessageBox(msg):
    root = tk.Tk()
    root.attributes('-topmost', True)  # 设置置顶
    root.withdraw()  # 隐藏临时窗口
    try:
        messagebox.showinfo("提示", msg)
    finally:
        root.destroy()  # 确保窗口被销毁



def showQuestion(msg):
    root = tk.Tk()
    root.attributes('-topmost', True)  # 设置置顶
    root.withdraw()  # 隐藏临时窗口
    try:
        return messagebox.askyesno("提示", msg)
    finally:
        root.destroy()  # 确保窗口被销毁


def showDirectoryDialog(parent_form):
    directory = filedialog.askdirectory(parent=parent_form, title="选择目录")
    return directory


def showSaveDialog(parent_form):
    file_path = filedialog.asksaveasfilename(
        parent=parent_form,
        title="保存文件",
        defaultextension=".xlsx",
        filetypes=[("Excel Files", "*.xlsx"), ("All Files", "*.*")]
    )
    return file_path


# 示例用法
if __name__ == "__main__":
    root = Tk()
    root.withdraw()  # 隐藏主窗口

    # 测试文件选择对话框
    file_path = showFileDialog(root)
    if file_path:
        showMessageBox(f"选择的文件: {file_path}")

    # 测试问题对话框
    if showQuestion("您要继续吗？"):
        showMessageBox("您选择了继续！")
    else:
        showMessageBox("您选择了不继续！")

    # 测试保存对话框
    save_path = showSaveDialog(root)
    if save_path:
        showMessageBox(f"保存的文件路径: {save_path}")

    root.mainloop()
