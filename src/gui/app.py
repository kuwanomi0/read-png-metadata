import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
from PIL.PngImagePlugin import PngImageFile
import os

try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    HAS_DND = True
except ImportError:
    HAS_DND = False

class PngMetadataViewer:
    def __init__(self):
        self.root = TkinterDnD.Tk() if HAS_DND else tk.Tk()
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

        # PanedWindowの作成（左右に分割）
        self.paned = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        self.paned.pack(expand=True, fill="both")

        # 左側：画像表示エリア
        self.image_frame = ttk.LabelFrame(self.paned, text="画像")

        self.image_label = ttk.Label(self.image_frame, text="ここに画像をドロップ")
        self.image_label.pack(expand=True, fill="both", padx=5, pady=5)

        # ドラッグ＆ドロップの設定
        if HAS_DND:
            self.image_label.drop_target_register(DND_FILES)
            self.image_label.dnd_bind('<<Drop>>', self._on_drop)

        # 右側：メタデータ表示エリア
        metadata_frame = ttk.LabelFrame(self.paned, text="メタデータ")

        # メタデータ表示のコントロールフレーム
        control_frame = ttk.Frame(metadata_frame)
        control_frame.pack(fill="x", padx=5, pady=(5,0))

        # 折り返しの設定用チェックボックス
        self.wrap_var = tk.BooleanVar(value=True)  # デフォルトで折り返し有効
        self.wrap_checkbox = ttk.Checkbutton(
            control_frame,
            text="テキストを折り返す",
            variable=self.wrap_var,
            command=self.toggle_text_wrap
        )
        self.wrap_checkbox.pack(side="left")

        # メタデータ表示用のテキストエリアとスクロールバー
        text_frame = ttk.Frame(metadata_frame)
        text_frame.pack(expand=True, fill="both", padx=5, pady=5)

        # テキストとスクロールバーを含むフレーム
        text_scrollbar_frame = ttk.Frame(text_frame)
        text_scrollbar_frame.pack(expand=True, fill="both")

        self.metadata_text = tk.Text(text_scrollbar_frame, wrap=tk.WORD)
        self.metadata_text.pack(side="left", expand=True, fill="both")

        # 縦スクロールバー
        v_scrollbar = ttk.Scrollbar(text_scrollbar_frame, orient="vertical", command=self.metadata_text.yview)
        v_scrollbar.pack(side="right", fill="y")
        self.metadata_text.configure(yscrollcommand=v_scrollbar.set)

        # 横スクロールバー（初期状態では非表示）
        self.h_scrollbar = ttk.Scrollbar(text_frame, orient="horizontal", command=self.metadata_text.xview)
        self.metadata_text.configure(xscrollcommand=self.h_scrollbar.set)

        # PanedWindowにペインを追加
        self.paned.add(self.image_frame, weight=1)  # weight=1で左ペインが伸縮可能に
        self.paned.add(metadata_frame, weight=1)    # weight=1で右ペインが伸縮可能に        # ステータスバー
        self.status_bar = ttk.Label(self.root, text="準備完了", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def _on_drop(self, event):
        """ドラッグ＆ドロップされたファイルを開く"""
        data = event.data
        if data.startswith('{'):
            path = data.split('}')[0][1:]
        else:
            path = data.split()[0]
        path = path.strip()
        if path:
            self.load_image(path)

    def open_image(self):
        file_path = filedialog.askopenfilename(
            title="PNG画像を選択",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
        )
        if not file_path:
            return
        self.load_image(file_path)

    def load_image(self, file_path):
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

    def toggle_text_wrap(self):
        """テキストの折り返し設定を切り替える"""
        if self.wrap_var.get():
            # 折り返しを有効にする
            self.metadata_text.configure(wrap=tk.WORD)
            self.h_scrollbar.pack_forget()  # 横スクロールバーを非表示
        else:
            # 折り返しを無効にする
            self.metadata_text.configure(wrap=tk.NONE)
            self.h_scrollbar.pack(side="bottom", fill="x")  # 横スクロールバーを表示

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = PngMetadataViewer()
    app.run()
