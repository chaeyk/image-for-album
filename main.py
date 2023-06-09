from PIL import Image, ImageDraw, ImageFont
from PIL.ExifTags import Base
import argparse
from os import listdir
from os.path import isfile, join
from pathlib import Path
import traceback
import re

# ratio1:ratio2 비율을 맞추려면 value1과 같은 비율의 value2는 얼마인가?
def ratioTarget(ratio1, ratio2, value1):
  return value1 * ratio2 / ratio1

def loadFont(fontfiles, image_width, image_height):
  # 이미지 크기가 1000 x 1334 일때 폰트 크기 60
  size_by_width = ratioTarget(1000, 60, image_width)
  size_by_height = ratioTarget(1334, 60, image_height)
  size = round(min(size_by_width, size_by_height))
  for fontfile in fontfiles:
    try:
      return ImageFont.truetype(fontfile, size)
    except:
      pass

def getImageDateTime(exif, filename):
  # exif 정보 사용
  if exif:
    if exif.get(Base.DateTimeOriginal.value):
      dt = exif[Base.DateTimeOriginal.value]
      if dt:
        return str(dt).replace(':', '-')[0:10]
    if exif.get(Base.DateTime.value):
      dt = exif[Base.DateTime.value]
      if dt:
        return str(dt).replace(':', '-')[0:10]

  # 파일명에서 추출
  if filename.regex('^(20\d{6})'):
    return f'{filename[0:4]}-{filename[4:6]-{filename[6:8]}}'

  # 없으면 끝
  return None

def processImage(filepath, filename, outpath, target_width, target_height):
  try:
    with Image.open(join(filepath, filename)) as image:
      exif = image._getexif()

      # 전자 앨범이 exif의 회전 정보를 처리하지 못한다.
      # exif 의 회전 정보에 따라 이미지 돌리고 exif 정보 삭제
      if exif and exif.get(Base.Orientation.value):
        if exif[Base.Orientation.value] == 3:
          image = image.rotate(180, expand=True)
          exif[Base.Orientation.value] = 0
        elif exif[Base.Orientation.value] == 6:
          image=image.rotate(270, expand=True)
          exif[Base.Orientation.value] = 0
        elif exif[Base.Orientation.value] == 8:
          image=image.rotate(90, expand=True)
          exif[Base.Orientation.value] = 0

      # 가로 세로 비율이 안맞으면 잘라서 맞춘다
      profitHeight = ratioTarget(target_width, target_height, image.width)
      if image.height > profitHeight:
        image = image.crop((0, (image.height - profitHeight) / 2, image.width, (image.height + profitHeight) / 2))

      profitWidth = ratioTarget(target_height, target_width, image.height)
      if image.width > profitWidth:
        image = image.crop(((image.width - profitWidth) / 2, 0, (image.width + profitWidth) / 2, image.height))

      # 이미지 크기 줄임
      if image.width > target_width:
        image = image.resize((target_width, target_height), Image.Resampling.BICUBIC)

      # 날짜 새기기
      dt = getImageDateTime(exif, filename)
      if dt:
        draw = ImageDraw.Draw(image)
        # 텍스트 출력할 위치
        pos_x = ratioTarget(1000, 70, image.width)
        pos_y = ratioTarget(1334, 50, image.height)
        draw.text((image.width - pos_x, image.height - pos_y), dt, font=font, anchor='rs', fill='orange', stroke_fill='black', stroke_width=2)

      Path(outpath).mkdir(parents=True, exist_ok=True)
      image.save(join(outpath, filename))
      print('reworked:', filename)
  except Exception as e:
    print('failed:', filename, '-', e)
    traceback.print_exc()

def parseSize(value):
  p = re.compile('^(\d+),(\d+)$')
  match = p.match(value)
  if not match:
    raise argparse.ArgumentTypeError('size must be in the format of "width,height"')

  return (int(match.group(1)), int(match.group(2)))

parser = argparse.ArgumentParser(description='image rotator')
parser.add_argument('filepath')
parser.add_argument('--outpath', default='output')
parser.add_argument('--size', type=parseSize, default='900,1200')
args = parser.parse_args()

if (isfile(args.filepath)):
  p = Path(args.filepath)
  filepath = p.parent
  filenames=[p.name]
else:
  filepath=args.filepath
  filenames=[]
  for f in listdir(filepath):
    filename = join(filepath, f)
    if (isfile(filename) and filename.endswith('.jpg')):
      filenames.append(f)

target_width = args.size[0]
target_height = args.size[1]

font = loadFont(['comic.ttf', 'arial.ttf'], target_width, target_height)

for filename in filenames:
  processImage(filepath, filename, args.outpath, target_width, target_height)
