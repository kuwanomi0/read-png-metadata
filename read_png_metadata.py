from PIL import Image
from PIL.PngImagePlugin import PngImageFile
import sys

def read_png_metadata(image_path):
    try:
        with Image.open(image_path) as img:
            if isinstance(img, PngImageFile):
                if img.text:
                    print(f"「{image_path}」のメタデータ:")
                    for k, v in img.text.items():
                        print(f"{k}: {v}")
                else:
                    print(f"「{image_path}」にメタデータは含まれていません。")
            else:
                print(f"「{image_path}」はPNGファイルではありません。")
    except FileNotFoundError:
        print(f"エラー: 「{image_path}」が見つかりません。")
    except Exception as e:
        print(f"エラー: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # コマンドライン引数で指定された画像を処理
        for image_path in sys.argv[1:]:
            read_png_metadata(image_path)
    else:
        print("使用方法: python read_png_metadata.py [画像パス1] [画像パス2] ...")
        print("例: python read_png_metadata.py image1.png image2.png")