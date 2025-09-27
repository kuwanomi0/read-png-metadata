import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
from PIL.PngImagePlugin import PngImageFile
import os

class PngMetadataViewer:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("PNG Metadata Viewer")
        self.root.geometry("800x600")
        self.create_menu()
        self.setup_gui()

    def create_menu(self):
        # メニューバーの作成
        self.menu_bar = tk.Menu(self.root)
        self.root.config(menu=self.menu_bar)

        # ファイルメニュー
        file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="ファイル", menu=file_menu)
        file_menu.add_command(label="画像を開く...", command=self.open_image, accelerator="Ctrl+O")
        file_menu.add_separator()
        file_menu.add_command(label="終了", command=self.root.quit, accelerator="Alt+F4")

        # ショートカットキーの設定
        self.root.bind("<Control-o>", lambda e: self.open_image())

    def setup_gui(self):
        # メインフレームの作成
        main_frame = ttk.Frame(self.root)
        main_frame.pack(expand=True, fill="both", padx=10, pady=10)

        # 左側：画像表示エリア
        self.image_frame = ttk.LabelFrame(main_frame, text="画像")
        self.image_frame.pack(side="left", expand=True, fill="both", padx=5, pady=5)

        self.image_label = ttk.Label(self.image_frame)
        self.image_label.pack(expand=True, fill="both", padx=5, pady=5)

        # 右側：メタデータ表示エリア
        metadata_frame = ttk.LabelFrame(main_frame, text="メタデータ")
        metadata_frame.pack(side="right", expand=True, fill="both", padx=5, pady=5)

        # メタデータ表示用のテキストエリア
        self.metadata_text = tk.Text(metadata_frame, wrap=tk.WORD, width=40)
        self.metadata_text.pack(expand=True, fill="both", padx=5, pady=5)

        # ステータスバー
        self.status_bar = ttk.Label(self.root, text="準備完了", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def open_image(self):
        file_path = filedialog.askopenfilename(
            title="PNG画像を選択",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
        )

        if not file_path:
            return

        try:
            with Image.open(file_path) as img:
                # メタデータの表示
                self.metadata_text.delete(1.0, tk.END)
                if isinstance(img, PngImageFile):
                    if img.text:
                        for k, v in img.text.items():
                            self.metadata_text.insert(tk.END, f"{k}: {v}\n")
                    else:
                        self.metadata_text.insert(tk.END, "メタデータは含まれていません。")
                else:
                    self.metadata_text.insert(tk.END, "この画像はPNGファイルではありません。")

                # 画像の表示（リサイズして表示）
                display_size = (400, 400)  # 表示サイズの最大値
                img.thumbnail(display_size, Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)

                self.image_label.configure(image=photo)
                self.image_label.image = photo  # 参照を保持

                # ステータスバーの更新
                file_name = os.path.basename(file_path)
                self.status_bar.config(text=f"画像を読み込みました: {file_name}")

        except Exception as e:
            messagebox.showerror("エラー", f"画像の読み込み中にエラーが発生しました：\n{str(e)}")
            self.status_bar.config(text="エラーが発生しました")

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = PngMetadataViewer()
    app.run()
