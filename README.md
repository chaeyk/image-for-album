# what is this

이미지가 회전된 상태로 저장되어 있고, exif tag로 회전 정보를 제공하고 있다면 그걸 풀어서 회전된 결과로 저장하는 프로그램. camel 전자 앨범이 회전되어 있는 이미지 파일을 처리하지 못하기 때문에 만들었다.

# requires

pillow 9.x 필요

```
pip3 install pillow
```

# usage

```
python3 main.py [--outpath path] target_path|target_file
```
