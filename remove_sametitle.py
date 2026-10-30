import os
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3

def remove_duplicate_by_tag_title(folder_path):
    # 폴더 존재 여부 확인
    if not os.path.exists(folder_path):
        print(f"오류: '{folder_path}' 폴더를 찾을 수 없습니다.")
        return

    # 태그 정보를 저장할 딕셔너리 {곡제목: (최대용량파일경로, 최대용량)}
    songs_dict = {}
    
    # 카운터 초기화
    total_scanned = 0
    deleted_count = 0
    no_tag_count = 0

    print("🎵 MP3 태그 스캔을 시작합니다 (하위 폴더 포함)...\n")

    # 하위 폴더까지 모두 탐색
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith('.mp3'):
                total_scanned += 1
                file_path = os.path.join(root, file)
                file_size = os.path.getsize(file_path)

                # MP3 태그에서 제목 추출 시도
                try:
                    audio = EasyID3(file_path)
                    # 제목 태그가 비어있지 않다면 첫 번째 값을 가져옴 (공백 제거)
                    title = audio['title'][0].strip() if 'title' in audio and audio['title'] else None
                except Exception:
                    # 태그가 없거나 깨진 경우 파일명을 대체용으로 사용하거나 건너뜀
                    title = None

                # 제목 태그가 없는 파일 처리
                if not title:
                    no_tag_count += 1
                    continue

                # 이미 동일한 '곡 제목'이 저장되어 있는 경우 (중복 발견)
                if title in songs_dict:
                    existing_path, existing_size = songs_dict[title]

                    # 현재 파일이 기존 파일보다 용량이 더 크다면 대체하고 기존 파일 삭제
                    if file_size > existing_size:
                        try:
                            os.remove(existing_path)
                            print(f"[삭제] 중복 곡 '{title}' - 용량이 작은 파일 제거:\n    ↳ {existing_path} ({existing_size} bytes)")
                            deleted_count += 1
                        except Exception as e:
                            print(f"[오류] 파일 삭제 실패: {existing_path} ({e})")
                        
                        # 딕셔너리 정보 업데이트
                        songs_dict[title] = (file_path, file_size)
                    
                    # 기존 파일이 더 크거나 같다면 현재 파일을 삭제
                    else:
                        try:
                            os.remove(file_path)
                            print(f"[삭제] 중복 곡 '{title}' - 용량이 작은 파일 제거:\n    ↳ {file_path} ({file_size} bytes)")
                            deleted_count += 1
                        except Exception as e:
                            print(f"[오류] 파일 삭제 실패: {file_path} ({e})")
                
                # 처음 발견된 곡 제목이라면 딕셔너리에 등록
                else:
                    songs_dict[title] = (file_path, file_size)

    print("\n✨ 작업 완료!")
    print(f"📊 총 스캔한 MP3 파일: {total_scanned}개")
    print(f"🗑️ 삭제된 중복 파일: {deleted_count}개")
    if no_tag_count > 0:
        print(f"⚠️ 제목 태그가 없어 건너뛴 파일: {no_tag_count}개")

# ⚠️ 사용법: 본인의 MP3 폴더 경로를 입력하세요.
target_folder = r"/home/getfree/음악/Melon Top 100"

# 프로그램 실행
remove_duplicate_by_tag_title(target_folder)

