from PIL import Image

def png_to_ico(input_file, output_file):
    with Image.open(input_file) as im:
        im.save(output_file, sizes=[(16, 16),(32, 32),(64, 64),(96, 96),(128, 128)])

# 使用示例：
png_to_ico("logo.png", "logo.ico")
