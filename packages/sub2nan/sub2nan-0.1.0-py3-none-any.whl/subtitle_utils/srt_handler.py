"""
SRT 자막 파일 처리를 위한 핸들러 클래스.

이 모듈은 SRT(SubRip Text) 형식의 자막 파일을 읽고, 수정하고, 저장하는
기능을 제공합니다. srt 라이브러리를 기반으로 구현되었습니다.
"""

from pathlib import Path
from typing import List, Optional, Union
import srt
import datetime

from .exceptions import SubtitleError, SubtitleParseError, SubtitleFileError


class SRTHandler:
    """
    SRT 자막 파일을 처리하는 핸들러 클래스.

    SRT 파일의 읽기, 쓰기, 수정 등의 기본적인 작업을 수행할 수 있으며,
    자막 항목들에 대한 편리한 접근 방법을 제공합니다.

    Attributes:
        subtitles (List[srt.Subtitle]): srt 자막 객체 리스트
        file_path (Optional[Path]): 현재 로드된 파일 경로
    """

    def __init__(self, file_path: Optional[Union[str, Path]] = None):
        """
        SRTHandler 인스턴스를 초기화합니다.

        Args:
            file_path: 로드할 SRT 파일 경로 (선택사항)

        Raises:
            SubtitleFileError: 파일을 찾을 수 없거나 읽을 수 없는 경우
            SubtitleParseError: 파일 형식이 올바르지 않은 경우
        """
        self.subtitles: List[srt.Subtitle] = []
        self.file_path: Optional[Path] = None

        if file_path:
            self.load(file_path)

    def load(self, file_path: Union[str, Path]) -> None:
        """
        SRT 파일을 로드합니다.

        Args:
            file_path: 로드할 SRT 파일의 경로

        Raises:
            SubtitleFileError: 파일을 찾을 수 없거나 읽을 수 없는 경우
            SubtitleParseError: 파일 형식이 올바르지 않은 경우
        """
        try:
            file_path = Path(file_path)

            if not file_path.exists():
                raise SubtitleFileError(f"파일을 찾을 수 없습니다: {file_path}")

            if not file_path.is_file():
                raise SubtitleFileError(f"지정된 경로가 파일이 아닙니다: {file_path}")

            # srt로 파일 로드
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            self.subtitles = list(srt.parse(content))
            self.file_path = file_path

        except srt.SRTParseError as e:
            raise SubtitleParseError(f"SRT 파일 파싱 오류: {e}")
        except (OSError, IOError) as e:
            raise SubtitleFileError(f"파일 읽기 오류: {e}")
        except UnicodeDecodeError as e:
            raise SubtitleFileError(f"파일 인코딩 오류: {e}")

    def save(self, file_path: Optional[Union[str, Path]] = None) -> None:
        """
        자막을 SRT 파일로 저장합니다.

        Args:
            file_path: 저장할 파일 경로. None인 경우 원본 파일에 덮어쓰기

        Raises:
            SubtitleFileError: 파일 저장 중 오류가 발생한 경우
            SubtitleError: 저장할 경로가 지정되지 않은 경우
        """
        try:
            if file_path:
                save_path = Path(file_path)
            elif self.file_path:
                save_path = self.file_path
            else:
                raise SubtitleError("저장할 파일 경로가 지정되지 않았습니다.")

            # 디렉토리가 존재하지 않으면 생성
            save_path.parent.mkdir(parents=True, exist_ok=True)

            # srt로 파일 저장
            with open(save_path, "w", encoding="utf-8") as f:
                f.write(srt.compose(self.subtitles))

            self.file_path = save_path

        except (OSError, IOError) as e:
            raise SubtitleFileError(f"파일 저장 오류: {e}")

    def get_subtitle_count(self) -> int:
        """
        자막 항목의 총 개수를 반환합니다.

        Returns:
            자막 항목의 개수
        """
        return len(self.subtitles)

    def get_subtitle(self, index: int) -> Optional[srt.Subtitle]:
        """
        지정된 인덱스의 자막 항목을 반환합니다.

        Args:
            index: 자막 항목의 인덱스 (0부터 시작)

        Returns:
            자막 항목 또는 None (인덱스가 범위를 벗어난 경우)
        """
        try:
            return self.subtitles[index]
        except IndexError:
            return None

    def add_subtitle(self, start_time: str, end_time: str, text: str) -> None:
        """
        새로운 자막 항목을 추가합니다.

        Args:
            start_time: 시작 시간 (형식: "HH:MM:SS,mmm")
            end_time: 종료 시간 (형식: "HH:MM:SS,mmm")
            text: 자막 텍스트

        Raises:
            SubtitleParseError: 시간 형식이 올바르지 않은 경우
        """
        try:
            # 시간 문자열을 timedelta로 변환
            start_td = self._time_string_to_timedelta(start_time)
            end_td = self._time_string_to_timedelta(end_time)

            # 새 인덱스 (1부터 시작)
            index = len(self.subtitles) + 1

            subtitle = srt.Subtitle(
                index=index, start=start_td, end=end_td, content=text
            )

            self.subtitles.append(subtitle)

        except ValueError as e:
            raise SubtitleParseError(f"자막 항목 생성 오류: {e}")

    def _time_string_to_timedelta(self, time_str: str) -> datetime.timedelta:
        """
        시간 문자열을 timedelta로 변환합니다.

        Args:
            time_str: 시간 문자열 (형식: "HH:MM:SS,mmm")

        Returns:
            timedelta 객체
        """
        try:
            # "HH:MM:SS,mmm" 형식을 파싱
            time_part, ms_part = time_str.split(",")
            hours, minutes, seconds = map(int, time_part.split(":"))
            milliseconds = int(ms_part)

            return datetime.timedelta(
                hours=hours, minutes=minutes, seconds=seconds, milliseconds=milliseconds
            )
        except (ValueError, IndexError) as e:
            raise ValueError(f"잘못된 시간 형식: {time_str}. 올바른 형식: HH:MM:SS,mmm")

    def get_duration(self) -> Optional[datetime.timedelta]:
        """
        전체 자막의 길이를 반환합니다.

        Returns:
            마지막 자막의 종료 시간 또는 None (자막이 없는 경우)
        """
        if not self.subtitles:
            return None
        return self.subtitles[-1].end

    def __len__(self) -> int:
        """자막 항목의 개수를 반환합니다."""
        return len(self.subtitles)

    def __getitem__(self, index: int) -> srt.Subtitle:
        """인덱스를 통한 자막 항목 접근을 지원합니다."""
        return self.subtitles[index]

    def __iter__(self):
        """자막 항목들에 대한 반복자를 제공합니다."""
        return iter(self.subtitles)
